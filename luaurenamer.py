import re
import sys
import time
import json
import socket
import random
import webbrowser
import threading
import argparse
import bisect
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

keywords = {
    "and", "break", "do", "else", "elseif", "end", "false", "for",
    "function", "if", "in", "local", "nil", "not", "or", "repeat",
    "return", "then", "true", "until", "while", "continue", "self"
}

libmethods = {
    "math.random":"MathRandom","math.randomseed":"MathRandomSeed","math.floor":"MathFloor","math.ceil":"MathCeil","math.abs":"MathAbs","math.clamp":"MathClamp","math.min":"MathMin","math.max":"MathMax","math.rad":"MathRad","math.deg":"MathDeg","math.sqrt":"MathSqrt","math.sin":"MathSin","math.cos":"MathCos","math.tan":"MathTan","math.asin":"MathAsin","math.acos":"MathAcos","math.atan":"MathAtan","math.atan2":"MathAtan2","math.sinh":"MathSinh","math.cosh":"MathCosh","math.tanh":"MathTanh","math.log":"MathLog","math.log10":"MathLog10","math.exp":"MathExp","math.pow":"MathPow","math.frexp":"MathFrexp","math.ldexp":"MathLdexp","math.modf":"MathModf","math.fmod":"MathFmod","math.noise":"MathNoise","math.round":"MathRound","math.sign":"MathSign","math.lerp":"MathLerp","math.map":"MathMap","math.huge":"MathHuge","math.pi":"MathPi","math.nan":"MathNaN",
    "table.insert":"TableInsert","table.remove":"TableRemove","table.concat":"TableConcat","table.find":"TableFind","table.sort":"TableSort","table.unpack":"TableUnpack","table.pack":"TablePack","table.create":"TableCreate","table.clear":"TableClear","table.clone":"TableClone","table.freeze":"TableFreeze","table.isfrozen":"TableIsFrozen","table.maxn":"TableMaxN","table.move":"TableMove","table.foreach":"TableForeach","table.foreachi":"TableForeachi","table.getn":"TableGetN",
    "string.format":"StringFormat","string.sub":"StringSub","string.upper":"StringUpper","string.lower":"StringLower","string.rep":"StringRep","string.split":"StringSplit","string.gsub":"StringGsub","string.match":"StringMatch","string.find":"StringFind","string.gmatch":"StringGmatch","string.len":"StringLen","string.byte":"StringByte","string.char":"StringChar","string.reverse":"StringReverse","string.pack":"StringPack","string.unpack":"StringUnpack","string.packsize":"StringPackSize","string.dump":"StringDump",
    "task.wait":"TaskWait","task.spawn":"TaskSpawn","task.delay":"TaskDelay","task.defer":"TaskDefer","task.cancel":"TaskCancel","task.synchronize":"TaskSync","task.desynchronize":"TaskDesync",
    "coroutine.create":"CoroutineCreate","coroutine.resume":"CoroutineResume","coroutine.yield":"CoroutineYield","coroutine.status":"CoroutineStatus","coroutine.wrap":"CoroutineWrap","coroutine.running":"CoroutineRunning","coroutine.isyieldable":"CoroutineIsYieldable","coroutine.close":"CoroutineClose",
    "os.time":"OsTime","os.date":"OsDate","os.clock":"OsClock","os.difftime":"OsDiffTime","os.getenv":"OsGetEnv",
    "utf8.char":"Utf8Char","utf8.codepoint":"Utf8CodePoint","utf8.len":"Utf8Len","utf8.offset":"Utf8Offset","utf8.codes":"Utf8Codes","utf8.graphemes":"Utf8Graphemes",
    "bit32.band":"Bit32Band","bit32.bor":"Bit32Bor","bit32.bxor":"Bit32Bxor","bit32.bnot":"Bit32Bnot","bit32.lshift":"Bit32LShift","bit32.rshift":"Bit32RShift","bit32.arshift":"Bit32ArShift","bit32.lrotate":"Bit32LRotate","bit32.rrotate":"Bit32RRotate","bit32.btest":"Bit32BTest","bit32.extract":"Bit32Extract","bit32.replace":"Bit32Replace","bit32.countlz":"Bit32CountLZ","bit32.countrz":"Bit32CountRZ",
    "debug.traceback":"DebugTraceback","debug.info":"DebugInfo","debug.getinfo":"DebugGetInfo","debug.profilebegin":"DebugProfileBegin","debug.profileend":"DebugProfileEnd","debug.getmemorycategory":"DebugGetMemoryCategory","debug.setmemorycategory":"DebugSetMemoryCategory","debug.resetmemorycategory":"DebugResetMemoryCategory","debug.upvalues":"DebugUpvalues","debug.getupvalue":"DebugGetUpvalue","debug.setupvalue":"DebugSetUpvalue","debug.getlocal":"DebugGetLocal","debug.setlocal":"DebugSetLocal","debug.getregistry":"DebugGetRegistry","debug.getmetatable":"DebugGetMetatable","debug.setmetatable":"DebugSetMetatable","debug.getfenv":"DebugGetFenv","debug.setfenv":"DebugSetFenv","debug.sethook":"DebugSetHook","debug.gethook":"DebugGetHook","debug.debug":"DebugDebug","debug.getuservalue":"DebugGetUserValue","debug.setuservalue":"DebugSetUserValue",
    "buffer.create":"BufferCreate","buffer.fromstring":"BufferFromString","buffer.tostring":"BufferToString","buffer.len":"BufferLen","buffer.copy":"BufferCopy","buffer.fill":"BufferFill","buffer.readi8":"BufferReadI8","buffer.readu8":"BufferReadU8","buffer.readi16":"BufferReadI16","buffer.readu16":"BufferReadU16","buffer.readi32":"BufferReadI32","buffer.readu32":"BufferReadU32","buffer.readf32":"BufferReadF32","buffer.readf64":"BufferReadF64","buffer.writei8":"BufferWriteI8","buffer.writeu8":"BufferWriteU8","buffer.writei16":"BufferWriteI16","buffer.writeu16":"BufferWriteU16","buffer.writei32":"BufferWriteI32","buffer.writeu32":"BufferWriteU32","buffer.writef32":"BufferWriteF32","buffer.writef64":"BufferWriteF64",
    "vector.create":"VectorCreate","vector.magnitude":"VectorMagnitude","vector.normalize":"VectorNormalize","vector.cross":"VectorCross","vector.dot":"VectorDot","vector.angle":"VectorAngle","vector.floor":"VectorFloor","vector.ceil":"VectorCeil","vector.abs":"VectorAbs","vector.sign":"VectorSign","vector.clamp":"VectorClamp","vector.min":"VectorMin","vector.max":"VectorMax","vector.zero":"VectorZero","vector.one":"VectorOne","vector.xAxis":"VectorXAxis","vector.yAxis":"VectorYAxis","vector.zAxis":"VectorZAxis",
    "json.encode":"JsonEncode","json.decode":"JsonDecode",
    "bit.band":"BitBand","bit.bor":"BitBor","bit.bxor":"BitBxor","bit.bnot":"BitBnot","bit.lshift":"BitLShift","bit.rshift":"BitRShift","bit.arshift":"BitArShift","bit.rol":"BitRol","bit.ror":"BitRor","bit.bswap":"BitBswap","bit.tohex":"BitToHex",
}

globalfunctions = {
    "pcall":"PcallOk","xpcall":"XpcallOk","assert":"Asserted","type":"TypeName","typeof":"TypeName","tostring":"ToString","tonumber":"ToNumber","ipairs":"IPairsIterator","pairs":"PairsIterator","next":"NextItem","select":"Selected","unpack":"Unpacked","rawget":"RawValue","rawset":"RawTable","rawequal":"RawEqual","rawlen":"RawLength","getmetatable":"Metatable","setmetatable":"WithMetatable","newproxy":"NewProxy","require":"Module","collectgarbage":"Collected","loadstring":"LoadedFunction","load":"LoadedFunction","getfenv":"GetFenv","setfenv":"SetFenv","getgenv":"GetGenv","getsenv":"GetScriptEnv","getrenv":"GetRobloxEnv","getreg":"GetRegistry","getmenv":"GetModuleEnv","error":"ErrorMessage","tick":"Tick","time":"Time","elapsedTime":"ElapsedTime","wait":"Elapsed","spawn":"Thread","delay":"Thread","settings":"Settings","stats":"Stats","print":"Printed","warn":"Warned","IsA":"IsType","writefile":"WriteFile","readfile":"ReadFile","appendfile":"AppendFile","makefolder":"MakeFolder","delfile":"DeleteFile","delfolder":"DeleteFolder","listfiles":"ListFiles","isfile":"IsFile","isfolder":"IsFolder","loadfile":"LoadFile","dofile":"DoFile","getupvalue":"GetUpvalue","getupvalues":"GetUpvalues","setupvalue":"SetUpvalue","upvalues":"Upvalues","getrawmetatable":"GetRawMetatable","setrawmetatable":"SetRawMetatable","hookfunction":"HookFunction","hookmetamethod":"HookMetamethod","getnamecallmethod":"GetNamecallMethod","setnamecallmethod":"SetNamecallMethod","checkcaller":"CheckCaller","islclosure":"IsLClosure","iscclosure":"IsCClosure","newcclosure":"NewCClosure","clonefunction":"CloneFunction","restorefunction":"RestoreFunction","getfunctionhash":"GetFunctionHash","getconstant":"GetConstant","getconstants":"GetConstants","getgc":"GetGC","getinstances":"GetInstances","getnilinstances":"GetNilInstances","getscripts":"GetScripts","getloadedmodules":"GetLoadedModules","getrunningscripts":"GetRunningScripts","fireclickdetector":"FireClickDetector","firetouchinterest":"FireTouchInterest","fireproximityprompt":"FireProximityPrompt","firesignal":"FireSignal","getconnections":"GetConnections","getcustomasset":"GetCustomAsset","getcallbackvalue":"GetCallbackValue","getrenderstepped":"GetRenderStepped","getheartbeat":"GetHeartbeat","getstepped":"GetStepped","identifyexecutor":"IdentifyExecutor","getexecutorname":"GetExecutorName","getscriptbytecode":"GetScriptBytecode","getscripthash":"GetScriptHash","getscriptclosure":"GetScriptClosure","getscriptfromthread":"GetScriptFromThread","request":"Request","httprequest":"HttpRequest","synrequest":"SynRequest","setclipboard":"SetClipboard","toclipboard":"ToClipboard","mouse1click":"Mouse1Click","mouse1press":"Mouse1Press","mouse1release":"Mouse1Release","mouse2click":"Mouse2Click","mouse2press":"Mouse2Press","mouse2release":"Mouse2Release","mousemoveabs":"MouseMoveAbs","mousemoverel":"MouseMoveRel","mousescroll":"MouseScroll","keypress":"KeyPress","keyrelease":"KeyRelease","keytap":"KeyTap","iskeydown":"IsKeyDown","iskeypressed":"IsKeyPressed","getmouseposition":"GetMousePosition","getmousestate":"GetMouseState","setfflag":"SetFFlag","getfflag":"GetFFlag","getthreadidentity":"GetThreadIdentity","setthreadidentity":"SetThreadIdentity","getidentity":"GetIdentity","setidentity":"SetIdentity","getcallingscript":"GetCallingScript","decompile":"Decompile","setreadonly":"SetReadOnly","isreadonly":"IsReadOnly","isexecutorclosure":"IsExecutorClosure","isexecutor":"IsExecutor","getactors":"GetActors","gethui":"GetHui","getimmersivemode":"GetImmersiveMode","setimmersivemode":"SetImmersiveMode","isrenderobj":"IsRenderObj","getrenderproperty":"GetRenderProperty","setrenderproperty":"SetRenderProperty","cleardrawcache":"ClearDrawCache","drawingnew":"DrawingNew","getscriptsource":"GetScriptSource","getmenv2":"GetModuleEnv2","getscriptthread":"GetScriptThread","getthreads":"GetThreads","getproperties":"GetProperties","getattributes":"GetAttributes","getsignals":"GetSignals","getprotos":"GetProtos","getupvals":"GetUpvalues","getrawproperty":"GetRawProperty","setrawproperty":"SetRawProperty","gethiddenproperty":"GetHiddenProperty","sethiddenproperty":"SetHiddenProperty","setcallbackvalue":"SetCallbackValue","writecustomasset":"WriteCustomAsset",
}

methodnames = {
    "Wait":"Elapsed","Connect":"Connection","Once":"Connection","ConnectParallel":"Connection","Clone":"Clone","Destroy":"Destroyed","ClearAllChildren":"Cleared","GetChildren":"Children","GetDescendants":"Descendants","GetPlayers":"PlayerList","GetTagged":"Tagged","GetInstanceAddedSignal":"Signal","GetInstanceRemovedSignal":"Signal","GetDataStore":"DataStore","GetOrderedDataStore":"OrderedDataStore","GetGlobalDataStore":"GlobalDataStore","GetCollisionGroupId":"GroupId","GetCollisionGroupName":"GroupName","CreatePath":"Path","Create":"Created","CreateWindow":"Window","JSONEncode":"Json","JSONDecode":"Decoded","HttpGetAsync":"Response","HttpPostAsync":"Response","HttpGet":"Response","HttpPost":"Response","PostAsync":"Response","RequestAsync":"Response","GenerateGUID":"Guid","GetAsync":"Value","SetAsync":"Value","UpdateAsync":"Value","IncrementAsync":"Value","Kick":"Kicked","GetMouse":"Mouse","GetPropertyChangedSignal":"Signal","GetAttributeChangedSignal":"Signal","GetAttribute":"Value","SetAttribute":"Attribute","GetPivot":"Pivot","PivotTo":"Pivot","GetFullName":"FullName","GetDebugId":"DebugId","FindFirstAncestor":"Ancestor","FindFirstAncestorOfClass":"Ancestor","FindFirstAncestorWhichIsA":"Ancestor","IsA":"IsType","AddTag":"Tag","RemoveTag":"Tag","HasTag":"HasTag","GetTags":"Tags","WaitForChild":"Child","FindFirstChild":"Child","FindFirstChildOfClass":"Child","FindFirstChildWhichIsA":"Child","SetPrimaryPartCFrame":"Pivot","GetPrimaryPartCFrame":"Pivot","MoveTo":"Pivot","LoadCharacter":"Character","LoadCharacterWithHumanoidDescription":"Character","GetRankInGroup":"Rank","GetRoleInGroup":"Role","IsInGroup":"IsInGroup","IsFriendsWith":"IsFriend","GetFriendsAsync":"Friends","GetUserIdFromNameAsync":"UserId","GetNameFromUserIdAsync":"UserName","GetUserThumbnailAsync":"Thumbnail","GetProductInfo":"ProductInfo","UserOwnsGamePassAsync":"OwnsGamePass","PromptGamePassPurchase":"Prompt","PromptProductPurchase":"Prompt","PromptPurchase":"Prompt","GetDeveloperProductsAsync":"Products","GetStorePages":"Pages","GetService":"Service",
}

signalparams = {
    "playeradded": ["Player"],
    "playerremoving": ["Player"],
    "characteradded": ["Character"],
    "characterremoving": ["Character"],
    "characterappearanceloaded": ["Character"],
    "inputbegan": ["Input", "GameProcessed"],
    "inputended": ["Input", "GameProcessed"],
    "inputchanged": ["Input", "GameProcessed"],
    "touchstarted": ["Touch", "GameProcessed"],
    "touchended": ["Touch", "GameProcessed"],
    "touchmoved": ["Touch", "GameProcessed"],
    "touchtap": ["TouchPositions", "GameProcessed"],
    "heartbeat": ["DeltaTime"],
    "renderstepped": ["DeltaTime"],
    "stepped": ["Time", "DeltaTime"],
    "touched": ["Hit"],
    "childadded": ["Child"],
    "childremoved": ["Child"],
    "descendantadded": ["Descendant"],
    "descendantremoving": ["Descendant"],
    "ancestrychanged": ["Child", "Parent"],
    "attributechanged": ["Property"],
    "changed": ["Property"],
    "healthchanged": ["Health"],
    "statechanged": ["OldState", "NewState"],
    "running": ["Speed"],
    "swimming": ["Speed"],
    "climbing": ["Speed"],
    "triggered": ["Player"],
    "triggerended": ["Player"],
    "mouseclick": ["Player"],
    "rightmouseclick": ["Player"],
    "mousehoverenter": ["Player"],
    "mousehoverleave": ["Player"],
    "onserverevent": ["Player"],
    "onserverinvoke": ["Player"],
    "focuslost": ["EnterPressed", "InputObject"],
    "dragstart": ["Player", "CursorRay", "ViewFrame"],
    "dragcontinue": ["Player", "CursorRay", "ViewFrame"],
    "dragend": ["Player"],
}

singularmap = {
    "PlayerList": "Player",
    "Players": "Player",
    "Children": "Child",
    "Descendants": "Descendant",
    "Tags": "Tag",
    "Tagged": "TaggedInstance",
    "Products": "Product",
    "Pages": "Page",
    "Friends": "Friend",
    "ListFiles": "FilePath",
    "GetConnections": "Connection",
    "GetInstances": "Inst",
    "GetNilInstances": "NilInst",
    "GetScripts": "ScriptObj",
    "GetRunningScripts": "RunningScript",
    "GetLoadedModules": "LoadedModule",
    "GetGC": "GcObj",
    "GetActors": "Actor",
    "GetThreads": "ThreadObj",
    "GetPlayingAnimationTracks": "AnimationTrack",
    "GetConnectedParts": "ConnectedPart",
    "GetJoints": "Joint",
    "GetAttributes": "AttributeValue",
    "GetProperties": "PropertyValue",
}

GENERIC_URL_SEGMENTS = {
    "http", "https", "www", "com", "org", "net", "io", "gg", "me", "dev", "menu", "xyz",
    "github", "githubusercontent", "raw", "gist", "gitlab", "bitbucket", "pastebin",
    "hastebin", "paste", "sirius", "luarmor", "api", "cdn", "main", "master", "heads",
    "refs", "tags", "blob", "tree", "releases", "release", "latest", "download",
    "downloads", "source", "src", "dist", "build", "out", "bin", "lib", "library",
    "init", "index", "loader", "load", "script", "scripts", "client", "server",
    "shared", "modules", "module", "packages", "package", "assets", "files", "file",
    "v1", "v2", "v3", "v4", "lua", "luau", "txt", "json", "addons", "addon", "plugins"
}

RE_SPLIT_CLASS = re.compile(r"[\s_\-]+")
RE_VALID_IDENT = re.compile(r"[A-Za-z_]\w*")
RE_PLACEHOLDER_1 = re.compile(r"[a-zA-Z]{1,3}\d+[a-zA-Z0-9_]*")
RE_PLACEHOLDER_2 = re.compile(r"_*(?:[a-zA-Z]_[a-zA-Z]_?\d+|[a-zA-Z]\d*_\d+|(?:var|arg|upval|func|tbl|tmp|local|param|reg|slot|const|idx|val)_?\d+)")
RE_URL = re.compile(r"https?://([^\s\"'`<>\)\]]+)", re.IGNORECASE)
RE_URL_EXT = re.compile(r"\.(?:luau|lua|txt|json|min|js)+$", re.IGNORECASE)
RE_NON_ALNUM = re.compile(r"[^A-Za-z0-9_\-]")
RE_VER_NUM = re.compile(r"v?\d+(?:\.\d+)*")


def normalizeclassname(name):
    parts = RE_SPLIT_CLASS.split(name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def isvalididentifier(s):
    return bool(RE_VALID_IDENT.fullmatch(s))


def safeident(n):
    if not n or not isvalididentifier(n):
        return None
    if n.lower() in keywords:
        return None
    return n


def isplaceholder(name):
    if not name or name == "_":
        return False
    return bool(RE_PLACEHOLDER_1.fullmatch(name) or RE_PLACEHOLDER_2.fullmatch(name))


def tocamel(name):
    if not name:
        return name
    return name[0].lower() + name[1:]


def joinsuffix(base, num):
    if base and base[-1].isdigit():
        return base + "_" + str(num)
    return base + str(num)


def infer_from_url(text):
    m = RE_URL.search(text)
    if not m:
        return None
    url_body = m.group(1).split("?", 1)[0].split("#", 1)[0].rstrip("/.,;:!)]}\"'")
    if "/" not in url_body:
        return None
    host, path = url_body.split("/", 1)
    raw_segs = [s for s in path.split("/") if s]
    if not raw_segs:
        return None

    cleaned = []
    for s in raw_segs:
        s = RE_URL_EXT.sub("", s)
        s = RE_NON_ALNUM.sub("", s)
        if s:
            cleaned.append(s)
    if not cleaned:
        return None

    host_l = host.lower()
    is_git_host = any(h in host_l for h in ("github", "githubusercontent", "gitlab", "bitbucket"))
    if is_git_host and len(cleaned) >= 2:
        for seg in reversed(cleaned[2:]):
            sl = seg.lower()
            if sl not in GENERIC_URL_SEGMENTS and not seg.isdigit() and not RE_VER_NUM.fullmatch(sl):
                return safeident(normalizeclassname(seg))
        repo = cleaned[1]
        if repo.lower() not in GENERIC_URL_SEGMENTS and not repo.isdigit():
            return safeident(normalizeclassname(repo))
        owner = cleaned[0]
        if owner.lower() not in GENERIC_URL_SEGMENTS and not owner.isdigit():
            return safeident(normalizeclassname(owner))

    for seg in reversed(cleaned):
        sl = seg.lower()
        if sl not in GENERIC_URL_SEGMENTS and not seg.isdigit() and not RE_VER_NUM.fullmatch(sl):
            return safeident(normalizeclassname(seg))
    return None


def readlongbracket(text, i):
    n = len(text)
    if i + 1 >= n or text[i] != "[":
        return -1
    j = i + 1
    eq = 0
    while j < n and text[j] == "=":
        eq += 1
        j += 1
    if j < n and text[j] == "[":
        close = "]" + "=" * eq + "]"
        end = text.find(close, j + 1)
        return n if end == -1 else end + len(close)
    return -1


def scanbacktick(text, start):
    i = start + 1
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "`":
            return ("done", i + 1)
        if c == "{":
            return ("interp", i + 1)
        i += 1
    return ("done", n)


def stripcomments(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ('"', "'", "`"):
            q = c
            start = i
            i += 1
            while i < n and text[i] != q:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                elif q != "`" and text[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and text[i] == q:
                i += 1
            out.append(text[start:i])
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            lb = readlongbracket(text, i + 2)
            if lb != -1:
                i = lb
            else:
                j = text.find("\n", i)
                i = n if j == -1 else j
            continue
        if c == "[":
            lb = readlongbracket(text, i)
            if lb != -1:
                out.append(text[i:lb])
                i = lb
                continue
        out.append(c)
        i += 1
    return "".join(out)


def startswithname(text, name):
    if not text or not name:
        return False
    text = stripcomments(text)
    stripped = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', text)
    stripped = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", stripped)
    m = re.match(r"^\s*([A-Za-z_]\w*)", stripped)
    return bool(m and m.group(1) == name)


def readstmt(code, start):
    i = start
    n = len(code)
    depth = 0
    blockdepth = 0
    exprifdepth = 0
    awaitingdo = False
    prev_word_or_op = "="
    while i < n:
        c = code[i]
        if c in " \t\r":
            i += 1
            continue
        if c in ('"', "'", "`"):
            q = c
            i += 1
            while i < n and code[i] != q:
                if code[i] == "\\" and i + 1 < n:
                    i += 2
                elif q != "`" and code[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and code[i] == q:
                i += 1
            prev_word_or_op = "str"
            continue
        if c == "-" and i + 1 < n and code[i + 1] == "-":
            lb = readlongbracket(code, i + 2)
            if lb != -1:
                i = lb
                continue
            j = code.find("\n", i)
            if depth == 0 and blockdepth == 0:
                return code[start:i], i
            i = n if j == -1 else j
            continue
        if c == "[":
            lb = readlongbracket(code, i)
            if lb != -1:
                i = lb
                prev_word_or_op = "str"
                continue
        if c in "([{":
            depth += 1
            prev_word_or_op = c
            i += 1
            continue
        if c in ")]}":
            if depth > 0:
                depth -= 1
                prev_word_or_op = c
                i += 1
                continue
            else:
                return code[start:i], i
        if c == ";" and depth == 0 and blockdepth == 0:
            return code[start:i], i
        if c == "\n" and depth == 0 and blockdepth == 0:
            return code[start:i], i
        if c.isalpha() or c == "_":
            wstart = i
            while i < n and (code[i].isalnum() or code[i] == "_"):
                i += 1
            w = code[wstart:i]
            if depth == 0:
                if w == "function":
                    blockdepth += 1
                elif w == "if":
                    if prev_word_or_op in ("=", ",", "(", "[", "{", "return", "and", "or", "not", "elseif", "then", "else", "+", "-", "*", "/", ".."):
                        exprifdepth += 1
                    else:
                        if blockdepth == 0:
                            return code[start:wstart], wstart
                        blockdepth += 1
                elif w in ("for", "while"):
                    if blockdepth == 0:
                        return code[start:wstart], wstart
                    awaitingdo = True
                    blockdepth += 1
                elif w == "do":
                    if blockdepth == 0:
                        return code[start:wstart], wstart
                    if awaitingdo:
                        awaitingdo = False
                    else:
                        blockdepth += 1
                elif w == "repeat":
                    if blockdepth == 0:
                        return code[start:wstart], wstart
                    blockdepth += 1
                elif w == "else":
                    if exprifdepth > 0 and blockdepth == 0:
                        exprifdepth -= 1
                    elif blockdepth == 0:
                        return code[start:wstart], wstart
                elif w == "elseif":
                    if exprifdepth == 0 and blockdepth == 0:
                        return code[start:wstart], wstart
                elif w in ("end", "until"):
                    if blockdepth > 0:
                        blockdepth -= 1
                    else:
                        return code[start:wstart], wstart
                elif w in ("local", "return", "break", "continue") and blockdepth == 0:
                    return code[start:wstart], wstart
            prev_word_or_op = w
            continue
        prev_word_or_op = c
        i += 1
    return code[start:n], n


def splitcommas(text):
    parts = []
    depth = 0
    last = 0
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ('"', "'", "`"):
            q = c
            i += 1
            while i < n and text[i] != q:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                elif q != "`" and text[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and text[i] == q:
                i += 1
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            lb = readlongbracket(text, i + 2)
            if lb != -1:
                i = lb
            else:
                j = text.find("\n", i)
                i = n if j == -1 else j
            continue
        if c == "[":
            lb = readlongbracket(text, i)
            if lb != -1:
                i = lb
                continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth > 0:
                depth -= 1
        elif c == "," and depth == 0:
            parts.append(text[last:i])
            last = i + 1
        i += 1
    parts.append(text[last:])
    return parts


def applymap(text, resolve_fn):
    if not resolve_fn:
        return text
    result = []
    i = 0
    n = len(text)
    interp_stack = []
    brace_stack = []
    while i < n:
        c = text[i]
        if c in ('"', "'"):
            start = i
            q = c
            i += 1
            while i < n and text[i] != q:
                if text[i] == "\\" and i + 1 < n:
                    i += 2
                elif text[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and text[i] == q:
                i += 1
            result.append(text[start:i])
            continue
        if c == "`":
            kind, stop = scanbacktick(text, i)
            result.append(text[i:stop])
            i = stop
            if kind == "interp":
                interp_stack.append(0)
            continue
        if c == "-" and i + 1 < n and text[i + 1] == "-":
            lb = readlongbracket(text, i + 2)
            if lb != -1:
                result.append(text[i:lb])
                i = lb
            else:
                j = text.find("\n", i)
                if j == -1:
                    j = n
                result.append(text[i:j])
                i = j
            continue
        if c == "[":
            lb = readlongbracket(text, i)
            if lb != -1:
                result.append(text[i:lb])
                i = lb
                continue
        if c == "{":
            if interp_stack:
                interp_stack[-1] += 1
            brace_stack.append("{")
            result.append(c)
            i += 1
            continue
        if c == "}":
            if brace_stack and brace_stack[-1] == "{":
                brace_stack.pop()
            if interp_stack and interp_stack[-1] == 0:
                interp_stack.pop()
                kind, stop = scanbacktick(text, i)
                result.append(text[i:stop])
                i = stop
                if kind == "interp":
                    interp_stack.append(0)
                continue
            elif interp_stack:
                interp_stack[-1] -= 1
            result.append(c)
            i += 1
            continue
        if c in "([":
            brace_stack.append(c)
            result.append(c)
            i += 1
            continue
        if c in ")]":
            if brace_stack:
                brace_stack.pop()
            result.append(c)
            i += 1
            continue
        if c.isalpha() or c == "_":
            m = RE_VALID_IDENT.match(text, i)
            word = m.group(0)
            k = i - 1
            while k >= 0 and text[k] in " \t\n\r":
                k -= 1
            isfield = (
                k >= 0
                and text[k] in ".:"
                and not (text[k] == "." and k >= 1 and text[k - 1] == ".")
            )
            r = i + len(word)
            while r < n and text[r] in " \t\n\r":
                r += 1
            istablekey = (
                brace_stack and brace_stack[-1] == "{"
                and k >= 0 and text[k] in "{,;"
                and r < n and text[r] == "="
                and (r + 1 >= n or text[r + 1] != "=")
            )
            if not isfield and not istablekey:
                rep = resolve_fn(word) if callable(resolve_fn) else resolve_fn.get(word)
                result.append(rep if rep is not None else word)
            else:
                result.append(word)
            i += len(word)
            continue
        result.append(c)
        i += 1
    return "".join(result)


def get_top_level_spans(e):
    matching_open = {}
    stack = []
    top_indices = []
    i = 0
    n = len(e)
    while i < n:
        c = e[i]
        if c in ('"', "'", "`"):
            q = c
            i += 1
            while i < n and e[i] != q:
                if e[i] == "\\" and i + 1 < n:
                    i += 2
                elif q != "`" and e[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and e[i] == q:
                i += 1
            continue
        if c == "[":
            lb = readlongbracket(e, i)
            if lb != -1:
                i = lb
                continue
        if c in "([{":
            stack.append((c, i))
            i += 1
            continue
        if c in ")]}":
            if stack:
                _, open_i = stack.pop()
                matching_open[i] = open_i
            i += 1
            continue
        if not stack:
            top_indices.append(i)
        i += 1
    return matching_open, set(top_indices)


def split_top_keyword(e, kw, top_set):
    pattern = re.compile(rf"\b{kw}\b")
    for m in pattern.finditer(e):
        if m.start() in top_set:
            return e[:m.start()].strip(), e[m.end():].strip()
    return None


def split_top_binop(e, top_set):
    i = 0
    n = len(e)
    while i < n:
        if i in top_set:
            if e[i:i+2] == ".." and (i + 2 >= n or e[i+2] != "."):
                return e[:i].strip(), e[i+2:].strip()
            if e[i] in "+*/%^":
                return e[:i].strip(), e[i+1:].strip()
            if e[i] == "-" and i > 0:
                k = i - 1
                while k >= 0 and e[k] in " \t\r\n":
                    k -= 1
                if k >= 0 and (e[k].isalnum() or e[k] in "_)]}\"'`"):
                    return e[:i].strip(), e[i+1:].strip()
        i += 1
    return None


def singularize_indexed(name):
    if not name:
        return name
    base = re.sub(r"_?\d+$", "", name)
    if base in singularmap:
        return singularmap[base]
    if base.endswith("List") and len(base) > 4:
        return base[:-4]
    if base.endswith("ies") and len(base) > 4:
        return base[:-3] + "y"
    if base.endswith("s") and not base.endswith("ss") and len(base) > 3:
        return base[:-1]
    return name


def infername(expr):
    e = stripcomments(expr).strip()
    while e.endswith(";"):
        e = e[:-1].strip()
    if not e:
        return None

    # Check if expression contains a URL inside loadstring / HttpGet / require / etc.
    if "http://" in e.lower() or "https://" in e.lower():
        url_hint = infer_from_url(e)
        if url_hint:
            return url_hint

    matching_open, top_set = get_top_level_spans(e)

    if e.startswith("(") and e.endswith(")") and matching_open.get(len(e) - 1) == 0:
        return infername(e[1:-1])

    if re.match(r"^if\b", e):
        sp_then = split_top_keyword(e[2:], "then", get_top_level_spans(e[2:])[1])
        if sp_then:
            after_then = sp_then[1]
            _, at_top = get_top_level_spans(after_then)
            sp_el = split_top_keyword(after_then, "elseif", at_top) or split_top_keyword(after_then, "else", at_top)
            if sp_el:
                return infername(sp_el[0]) or infername(sp_el[1])

    sp_or = split_top_keyword(e, "or", top_set)
    if sp_or:
        left_or, right_or = sp_or
        _, left_top = get_top_level_spans(left_or)
        sp_and = split_top_keyword(left_or, "and", left_top)
        if sp_and:
            cond_and, val_and = sp_and
            return infername(val_and) or infername(cond_and) or infername(right_or)
        return infername(left_or) or infername(right_or)

    sp_and = split_top_keyword(e, "and", top_set)
    if sp_and:
        left_and, right_and = sp_and
        return infername(right_and) or infername(left_and)

    sp_bin = split_top_binop(e, top_set)
    if sp_bin:
        left_b, right_b = sp_bin
        if left_b and right_b:
            return infername(left_b) or infername(right_b)

    if e.startswith("#") or (e.startswith("-") and not e[1:2].isdigit()):
        return infername(e[1:].strip())
    m_not = re.match(r"^not\b\s*(.+)$", e, re.DOTALL)
    if m_not:
        return infername(m_not.group(1))

    if re.match(r"^function\s*\(", e):
        return "Func"

    m = re.match(r'^["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*$', e)
    if m:
        return safeident(normalizeclassname(m.group(1)))

    had_array_index = False
    while e.endswith("]"):
        open_b = matching_open.get(len(e) - 1, -1)
        if open_b <= 0:
            break
        inside = e[open_b + 1 : -1].strip()
        if re.match(r'^["\']([A-Za-z_][A-Za-z0-9_]*)["\']$', inside):
            break
        e = e[:open_b].strip()
        had_array_index = True
        matching_open, top_set = get_top_level_spans(e)

    def finalize(res):
        if not res:
            return None
        if had_array_index:
            res = singularize_indexed(res)
        return safeident(res)

    if e.endswith(")"):
        open_p = matching_open.get(len(e) - 1, -1)
        if open_p == 0:
            return finalize(infername(e[1:-1]))
        if open_p > 0:
            callee = e[:open_p].strip()
            args_str = e[open_p + 1 : -1].strip()

            if re.search(r'(?:^|[.:]\s*)GetService$', callee):
                m_arg = re.match(r'^["\']([^"\']+)["\']', args_str)
                if m_arg:
                    return finalize(normalizeclassname(m_arg.group(1)))

            if re.match(r'^(?:Instance|Drawing)\s*\.\s*new$', callee):
                m_arg = re.match(r'^["\']([^"\']+)["\']', args_str)
                if m_arg:
                    return finalize(normalizeclassname(m_arg.group(1)))

            m_find = re.search(r'[.:]\s*(WaitForChild|FindFirstChild|FindFirstChildOfClass|FindFirstChildWhichIsA)$', callee)
            if m_find:
                m_arg = re.match(r'^["\']([^"\']+)["\']', args_str)
                if m_arg:
                    cname = normalizeclassname(m_arg.group(1))
                    if cname.lower() in keywords:
                        cname = cname + "Child"
                    return finalize(cname)

            m_dt = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)$', callee)
            if m_dt:
                dt, method = m_dt.group(1), m_dt.group(2)
                if method == "new" or method.startswith("from") or method.startswith("look") or method in ("Angles", "identity"):
                    n = dt
                else:
                    n = normalizeclassname(method)
                return finalize(n)

            m_lib = re.match(r'^([a-z_]\w*)\s*\.\s*([a-zA-Z_]\w*)$', callee)
            if m_lib:
                key = f"{m_lib.group(1)}.{m_lib.group(2)}"
                if key in libmethods:
                    return finalize(libmethods[key])
                if m_lib.group(2) in globalfunctions:
                    return finalize(globalfunctions[m_lib.group(2)])
                return finalize(normalizeclassname(m_lib.group(2)))

            m_fn = re.match(r'^([A-Za-z_]\w*)$', callee)
            if m_fn:
                fn = m_fn.group(1)
                n = globalfunctions.get(fn, fn)
                return finalize(n)

            m_meth = re.search(r'[.:]\s*([A-Za-z_]\w*)$', callee)
            if m_meth:
                method = m_meth.group(1)
                if method == "Wait":
                    if re.search(r'CharacterAdded\s*:\s*Wait$', callee):
                        return finalize("Character")
                    if re.search(r'PlayerAdded\s*:\s*Wait$', callee):
                        return finalize("Player")
                    if re.search(r'ChildAdded\s*:\s*Wait$', callee):
                        return finalize("Child")
                n = methodnames.get(method, normalizeclassname(method))
                return finalize(n)

            if callee.endswith(")"):
                return finalize(infername(callee))

    m = re.match(r'^Enum\s*\.\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        t, v = m.group(1), m.group(2)
        n = (t + v) if (len(v) <= 1 or v.lower() in keywords) else v
        return finalize(n)

    m = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        return finalize(normalizeclassname(m.group(2)))

    m = re.match(r'^([a-z_]\w*)\s*\.\s*([a-zA-Z_]\w*)\s*$', e)
    if m:
        key = f"{m.group(1)}.{m.group(2)}"
        if key in libmethods:
            return finalize(libmethods[key])

    m = re.search(r'\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*$', e)
    if m:
        field = m.group(1)
        n = field[0].upper() + field[1:] if field[0].islower() else field
        if n.lower() in keywords:
            n = n + "Prop"
        return finalize(n)

    m = re.search(r'\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]\s*$', e)
    if m:
        field = m.group(1)
        n = field[0].upper() + field[1:] if field[0].islower() else field
        if n.lower() in keywords:
            n = n + "Field"
        return finalize(n)

    m = re.match(r'^([a-zA-Z_]\w*)\s*$', e)
    if m:
        name = m.group(1)
        if name.lower() in keywords:
            return None
        n = name[0].upper() + name[1:] if name[0].islower() else name
        return finalize(n)

    return None


def tokenize(code):
    tokens = []
    i = 0
    n = len(code)
    interp_stack = []
    while i < n:
        c = code[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == "-" and i + 1 < n and code[i + 1] == "-":
            start = i
            lb = readlongbracket(code, i + 2)
            if lb != -1:
                i = lb
            else:
                end = code.find("\n", i)
                i = n if end == -1 else end
            tokens.append(("comment", code[start:i], start, i))
            continue
        if c in ('"', "'"):
            start = i
            q = c
            i += 1
            while i < n and code[i] != q:
                if code[i] == "\\" and i + 1 < n:
                    i += 2
                elif code[i] == "\n":
                    break
                else:
                    i += 1
            if i < n and code[i] == q:
                i += 1
            tokens.append(("string", code[start:i], start, i))
            continue
        if c == "`":
            kind, stop = scanbacktick(code, i)
            tokens.append(("string", code[i:stop], i, stop))
            i = stop
            if kind == "interp":
                interp_stack.append(0)
            continue
        if c == "{":
            if interp_stack:
                interp_stack[-1] += 1
            tokens.append(("op", "{", i, i + 1))
            i += 1
            continue
        if c == "}":
            if interp_stack and interp_stack[-1] == 0:
                interp_stack.pop()
                kind, stop = scanbacktick(code, i)
                tokens.append(("string", code[i:stop], i, stop))
                i = stop
                if kind == "interp":
                    interp_stack.append(0)
                continue
            elif interp_stack:
                interp_stack[-1] -= 1
            tokens.append(("op", "}", i, i + 1))
            i += 1
            continue
        if c == "[":
            lb = readlongbracket(code, i)
            if lb != -1:
                tokens.append(("string", code[i:lb], i, lb))
                i = lb
                continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (code[i].isalnum() or code[i] == "_"):
                i += 1
            word = code[start:i]
            tokens.append(("kw" if word in keywords else "ident", word, start, i))
            continue
        if c.isdigit() or (c == "." and i + 1 < n and code[i + 1].isdigit()):
            start = i
            while i < n and (code[i].isalnum() or code[i] in "._"):
                i += 1
            tokens.append(("num", code[start:i], start, i))
            continue
        tokens.append(("op", c, i, i + 1))
        i += 1
    return tokens


def prev_noncomment(tokens, ti):
    k = ti - 1
    while k >= 0 and tokens[k][0] == "comment":
        k -= 1
    return k


def next_noncomment(tokens, ti, n):
    k = ti + 1
    while k < n and tokens[k][0] == "comment":
        k += 1
    return k


def is_dot_or_colon_access(tokens, ti):
    pk = prev_noncomment(tokens, ti)
    if pk < 0:
        return False
    pt = tokens[pk]
    if pt[0] != "op" or pt[1] not in ".:":
        return False
    if pt[1] == ".":
        pk2 = prev_noncomment(tokens, pk)
        if pk2 >= 0 and tokens[pk2][0] == "op" and tokens[pk2][1] == "." and tokens[pk2][3] == pt[2]:
            return False
    return True


def findscopes(tokens, code):
    scopes = []
    stack = []
    awaitingdo = False
    n = len(tokens)
    for ti, tok in enumerate(tokens):
        if tok[0] != "kw":
            continue
        w = tok[1]
        if w in ("for", "while"):
            awaitingdo = True
            stack.append(("loop", ti, ti))
        elif w == "do":
            if awaitingdo:
                awaitingdo = False
            else:
                stack.append(("do", ti, ti))
        elif w == "function":
            stack.append(("func", ti, ti))
        elif w == "repeat":
            stack.append(("repeat", ti, ti))
        elif w == "if":
            pk = prev_noncomment(tokens, ti)
            is_expr_if = False
            if pk >= 0:
                pt = tokens[pk]
                if pt[0] == "op" and pt[1] in "=,([]{+-*/%^<>~":
                    is_expr_if = True
                elif pt[0] == "kw" and pt[1] in ("return", "and", "or", "not", "elseif", "then", "else", "while", "until", "in"):
                    is_expr_if = True
            if is_expr_if:
                stack.append(("expr_if", ti, ti))
            else:
                stack.append(("if", ti, ti))
        elif w == "elseif":
            if stack and stack[-1][0] == "if":
                kind, openti, branchstart = stack.pop()
                scopes.append((branchstart, ti))
                stack.append(("if", openti, ti))
        elif w == "else":
            if stack and stack[-1][0] == "expr_if":
                stack.pop()
            elif stack and stack[-1][0] == "if":
                kind, openti, branchstart = stack.pop()
                scopes.append((branchstart, ti))
                stack.append(("if", openti, ti))
        elif w == "end":
            while stack and stack[-1][0] == "expr_if":
                stack.pop()
            if stack:
                kind, openti, branchstart = stack.pop()
                scopes.append((branchstart, ti))
        elif w == "until":
            while stack and stack[-1][0] == "expr_if":
                stack.pop()
            if stack:
                kind, openti, branchstart = stack.pop()
                _, cond_end_pos = readstmt(code, tok[3])
                end_ti = ti + 1
                while end_ti < n and tokens[end_ti][2] < cond_end_pos:
                    end_ti += 1
                scopes.append((branchstart, end_ti))
    return scopes


def compute_table_key_tokens(tokens, n):
    table_keys = set()
    bracket_stack = []
    for ti, tok in enumerate(tokens):
        if tok[0] == "op":
            if tok[1] in "([{":
                bracket_stack.append(tok[1])
            elif tok[1] in ")]}" and bracket_stack:
                bracket_stack.pop()
        elif tok[0] == "ident":
            if bracket_stack and bracket_stack[-1] == "{":
                pk = prev_noncomment(tokens, ti)
                nk = next_noncomment(tokens, ti, n)
                if pk >= 0 and nk < n:
                    pt = tokens[pk]
                    nt = tokens[nk]
                    if pt[0] == "op" and pt[1] in "{,;" and nt[0] == "op" and nt[1] == "=":
                        nk2 = next_noncomment(tokens, nk, n)
                        if nk2 >= n or not (tokens[nk2][0] == "op" and tokens[nk2][1] == "="):
                            table_keys.add(ti)
    return table_keys


def skip_type_annotation(tokens, j, n):
    k = next_noncomment(tokens, j, n)
    depth = 0
    type_hint = None
    while k < n:
        t = tokens[k]
        if t[0] == "comment":
            k += 1
            continue
        if depth == 0:
            if t[0] == "op" and t[1] in ",=;)":
                break
            if t[0] == "kw" and t[1] not in ("nil", "true", "false", "function"):
                break
        if t[0] == "op":
            if t[1] in "([{<":
                depth += 1
            elif t[1] in ")]}>":
                if depth > 0:
                    depth -= 1
                else:
                    break
        elif t[0] == "ident" and depth == 0 and type_hint is None:
            if t[1].lower() not in ("any", "unknown", "never", "nil"):
                type_hint = normalizeclassname(t[1])
        k += 1
    return type_hint, k


def collectassigns(tokens, code, n, table_keys):
    assigns = {}
    ti = 0
    while ti < n - 1:
        tok = tokens[ti]
        if tok[0] == "kw" and tok[1] == "local":
            j = next_noncomment(tokens, ti, n)
            while j < n:
                t = tokens[j]
                if t[0] == "ident":
                    j = next_noncomment(tokens, j, n)
                    if j < n and tokens[j][0] == "op" and tokens[j][1] == ":":
                        _, j = skip_type_annotation(tokens, j, n)
                    if j < n and tokens[j][0] == "op" and tokens[j][1] == ",":
                        j = next_noncomment(tokens, j, n)
                        continue
                    break
                else:
                    break
            ti = j + 1
            continue

        if tok[0] != "ident" or ti in table_keys or is_dot_or_colon_access(tokens, ti):
            ti += 1
            continue
        nk = next_noncomment(tokens, ti, n)
        if nk >= n:
            break
        op1 = tokens[nk]
        if op1[0] != "op" or op1[1] != "=":
            ti += 1
            continue
        nk2 = next_noncomment(tokens, nk, n)
        if nk2 < n and tokens[nk2][0] == "op" and tokens[nk2][1] == "=":
            ti = nk2 + 1
            continue
        pk = prev_noncomment(tokens, ti)
        if pk >= 0:
            prev = tokens[pk]
            if prev[0] == "kw" and prev[1] in ("for", "local"):
                ti += 1
                continue
            if prev[0] == "op" and prev[1] in "~<>":
                ti += 1
                continue
        rhsstart = op1[3]
        rhstext, _ = readstmt(code, rhsstart)
        assigns.setdefault(tok[1], []).append((ti, rhstext))
        ti = nk + 1
    return assigns


def infer_multireturn(rhs_expr, idx):
    e = stripcomments(rhs_expr).strip()
    if re.match(r"^(?:pcall|xpcall)\s*\(", e):
        if idx == 1:
            m_ret = re.search(r"\breturn\s+(.+?)\s+end\s*[,)]", e, re.DOTALL)
            if m_ret:
                cand = infername(m_ret.group(1))
                if cand:
                    return cand
            return "Result"
        return f"Result{idx}"
    if re.search(r":\s*GetBoundingBox\s*\(\s*\)$", e):
        if idx == 1:
            return "Size"
    if re.match(r"^string\s*\.\s*find\s*\(", e):
        if idx == 1:
            return "EndIndex"
        if idx >= 2:
            return "Capture"
    if re.match(r"^Color3\s*\.\s*toHSV\s*\(", e):
        if idx == 1:
            return "Saturation"
        if idx == 2:
            return "Value"
    return infername(e)


def infer_param_from_usage(tokens, code, param_name, body_start_ti, body_end_ti, n):
    player_members = {
        "Character", "UserId", "DisplayName", "AccountAge", "Team", "TeamColor",
        "PlayerGui", "Backpack", "PlayerScripts", "StarterGear", "GetMouse", "Kick",
        "GetRankInGroup", "GetRoleInGroup", "IsInGroup", "IsFriendsWith", "LoadCharacter"
    }
    humanoid_members = {
        "Health", "MaxHealth", "WalkSpeed", "JumpPower", "JumpHeight", "HipHeight",
        "TakeDamage", "ChangeState", "GetState", "LoadAnimation", "EquipTool", "UnequipTools"
    }
    input_members = {"KeyCode", "UserInputType", "UserInputState", "Delta"}
    part_members = {
        "CFrame", "Anchored", "CanCollide", "Transparency", "BrickColor", "Material",
        "AssemblyLinearVelocity", "AssemblyAngularVelocity", "ApplyImpulse"
    }
    inst_members = {
        "Parent", "ClassName", "GetChildren", "GetDescendants", "FindFirstChild",
        "WaitForChild", "Destroy", "Clone", "GetAttribute", "SetAttribute"
    }
    for ti in range(body_start_ti, min(body_end_ti, n)):
        tok = tokens[ti]
        if tok[0] != "ident" or tok[1] != param_name:
            continue
        if is_dot_or_colon_access(tokens, ti):
            continue
        nk = next_noncomment(tokens, ti, n)
        if nk < n and tokens[nk][0] == "op" and tokens[nk][1] in ".:":
            nk2 = next_noncomment(tokens, nk, n)
            if nk2 < n and tokens[nk2][0] == "ident":
                mem = tokens[nk2][1]
                if mem in ("WaitForChild", "FindFirstChild"):
                    nk3 = next_noncomment(tokens, nk2, n)
                    if nk3 < n and tokens[nk3][0] == "op" and tokens[nk3][1] == "(":
                        nk4 = next_noncomment(tokens, nk3, n)
                        if nk4 < n and tokens[nk4][0] == "string":
                            sval = tokens[nk4][1].strip("\"'`")
                            if sval in ("Humanoid", "HumanoidRootPart", "Head", "Torso", "UpperTorso"):
                                return "Character"
                            if sval in ("PlayerGui", "Backpack", "PlayerScripts", "StarterGear"):
                                return "Player"
                if mem == "IsA":
                    nk3 = next_noncomment(tokens, nk2, n)
                    if nk3 < n and tokens[nk3][0] == "op" and tokens[nk3][1] == "(":
                        nk4 = next_noncomment(tokens, nk3, n)
                        if nk4 < n and tokens[nk4][0] == "string":
                            sval = tokens[nk4][1].strip("\"'`")
                            cname = normalizeclassname(sval)
                            if safeident(cname):
                                return cname
                if mem in player_members:
                    return "Player"
                if mem in humanoid_members:
                    return "Humanoid"
                if mem in input_members:
                    return "Input"
                if mem in part_members:
                    return "Part"
                if mem in inst_members:
                    return "Inst"
        elif nk < n and tokens[nk][0] == "op" and tokens[nk][1] == "(":
            return "Callback"
        elif nk < n and tokens[nk][0] == "op" and tokens[nk][1] in "+-*/%^":
            return "Num"
    return "Arg"


def renamecode(code):
    tokens = tokenize(code)
    n = len(tokens)
    if n == 0:
        return code

    scopes = findscopes(tokens, code)
    scopes.sort()
    scopestarts = [s[0] for s in scopes]

    def scopeendfor(ti):
        pos = bisect.bisect_right(scopestarts, ti) - 1
        while pos >= 0:
            s, e = scopes[pos]
            if e > ti:
                return e
            pos -= 1
        return n

    def scopechainof(ti):
        chain = [sid for sid, (s, e) in enumerate(scopes) if s <= ti < e]
        chain.sort(key=lambda sid: scopes[sid][0])
        return chain

    table_keys = compute_table_key_tokens(tokens, n)
    assigns = collectassigns(tokens, code, n, table_keys)

    declared_vars = []
    for ti_scan, tok_scan in enumerate(tokens):
        if tok_scan[0] == "kw" and tok_scan[1] == "local":
            j = next_noncomment(tokens, ti_scan, n)
            if j < n and tokens[j][0] == "kw" and tokens[j][1] == "function":
                fn_ti = next_noncomment(tokens, j, n)
                if fn_ti < n and tokens[fn_ti][0] == "ident":
                    if not isplaceholder(tokens[fn_ti][1]):
                        declared_vars.append((tokens[fn_ti][1], fn_ti, scopeendfor(ti_scan)))
            else:
                while j < n:
                    if tokens[j][0] == "ident":
                        if not isplaceholder(tokens[j][1]):
                            declared_vars.append((tokens[j][1], j, scopeendfor(ti_scan)))
                        j = next_noncomment(tokens, j, n)
                        if j < n and tokens[j][0] == "op" and tokens[j][1] == ":":
                            _, j = skip_type_annotation(tokens, j, n)
                        if j < n and tokens[j][0] == "op" and tokens[j][1] == ",":
                            j = next_noncomment(tokens, j, n)
                            continue
                    break

    scopeused = {}
    renames = []
    renames_by_old = {}

    def add_rename(oldname, newname, declti, activeti, scopeendti):
        rule = (oldname, newname, declti, activeti, scopeendti)
        renames.append(rule)
        renames_by_old.setdefault(oldname, []).append(rule)

    def make_resolver(at_ti):
        def resolve(word):
            rules = renames_by_old.get(word)
            if not rules:
                return None
            for idx_r in range(len(rules) - 1, -1, -1):
                _, nn, _, act, et = rules[idx_r]
                if act <= at_ti < et:
                    return nn
            return None
        return resolve

    def pick_candidate(newname, oldname, nameti, scopeendti, shadow):
        chain = scopechainof(nameti)
        seenchain = set(scopeused.get(-1, set()))
        for sid in chain:
            seenchain |= scopeused.get(sid, set())
        for (decl_name, d_ti, d_end) in declared_vars:
            if d_ti != nameti and decl_name != oldname and not (d_end <= nameti or d_ti >= scopeendti):
                seenchain.add(decl_name)

        if shadow or newname in keywords:
            candidate = joinsuffix(newname, 2)
            suffix = 3
        else:
            candidate = newname
            suffix = 2
        while candidate in seenchain or candidate in keywords or (candidate == oldname and shadow):
            candidate = joinsuffix(newname, suffix)
            suffix += 1

        if chain:
            innermost = chain[-1]
        else:
            innermost = -1
        scopeused.setdefault(innermost, set()).add(candidate)
        return candidate

    ti = 0
    while ti < n:
        tok = tokens[ti]

        if tok[0] == "kw" and tok[1] == "local":
            j = next_noncomment(tokens, ti, n)

            if j < n and tokens[j][0] == "kw" and tokens[j][1] == "function":
                fn_ti = next_noncomment(tokens, j, n)
                if fn_ti < n and tokens[fn_ti][0] == "ident":
                    oldname = tokens[fn_ti][1]
                    outer_scope_end = scopeendfor(ti)
                    if isplaceholder(oldname):
                        newname = "func"
                        candidate = pick_candidate(newname, oldname, fn_ti, outer_scope_end, False)
                        add_rename(oldname, candidate, fn_ti, fn_ti, outer_scope_end)
                    else:
                        chain = scopechainof(fn_ti)
                        innermost = chain[-1] if chain else -1
                        scopeused.setdefault(innermost, set()).add(oldname)
                        add_rename(oldname, oldname, fn_ti, fn_ti, outer_scope_end)
                ti = j
                continue

            names = []
            while j < n:
                t = tokens[j]
                if t[0] == "ident":
                    ident_ti = j
                    ident_name = t[1]
                    type_hint = None
                    j = next_noncomment(tokens, j, n)
                    if j < n and tokens[j][0] == "op" and tokens[j][1] == ":":
                        type_hint, j = skip_type_annotation(tokens, j, n)
                    names.append((ident_ti, ident_name, type_hint))
                    if j < n and tokens[j][0] == "op" and tokens[j][1] == ",":
                        j = next_noncomment(tokens, j, n)
                        continue
                    else:
                        break
                else:
                    break

            if not names:
                ti += 1
                continue

            haseq = j < n and tokens[j][0] == "op" and tokens[j][1] == "="
            after_rhs_ti = j
            if haseq:
                rhsstart = tokens[j][3]
                rhstext, rhsend_pos = readstmt(code, rhsstart)
                rhsparts = splitcommas(rhstext)
                first_fn_in_rhs = n
                k_scan = j + 1
                while k_scan < n and tokens[k_scan][2] < rhsend_pos:
                    if tokens[k_scan][0] == "kw" and tokens[k_scan][1] == "function":
                        first_fn_in_rhs = k_scan
                        break
                    k_scan += 1
                after_rhs_ti = min(k_scan, first_fn_in_rhs)
            else:
                rhsparts = []

            scopeendti = scopeendfor(ti)

            for idx, (nameti, oldname, type_hint) in enumerate(names):
                if oldname == "_":
                    continue
                if oldname.startswith("_") and not isplaceholder(oldname):
                    continue

                rawname = None
                swappedrhs = None

                if haseq:
                    resolver = make_resolver(nameti)
                    if idx < len(rhsparts):
                        swappedrhs = applymap(rhsparts[idx], resolver)
                        rawname = infername(swappedrhs)
                    elif len(rhsparts) == 1:
                        swappedrhs = applymap(rhsparts[0], resolver)
                        rawname = infer_multireturn(swappedrhs, idx)

                if not rawname and type_hint:
                    rawname = safeident(type_hint)

                if not rawname:
                    for (ati, atext) in assigns.get(oldname, []):
                        if nameti < ati < scopeendti:
                            resolver = make_resolver(ati)
                            swapped = applymap(atext, resolver)
                            cand = infername(swapped)
                            if cand:
                                rawname = cand
                                swappedrhs = swapped
                                break

                if not rawname and swappedrhs is not None:
                    stripped_rhs = stripcomments(swappedrhs).strip()
                    if re.match(r"^\{.*\}$", stripped_rhs, re.DOTALL) and isplaceholder(oldname):
                        rawname = "Tbl"

                if not rawname:
                    chain = scopechainof(nameti)
                    innermost = chain[-1] if chain else -1
                    scopeused.setdefault(innermost, set()).add(oldname)
                    add_rename(oldname, oldname, nameti, after_rhs_ti, scopeendti)
                    continue

                newname = tocamel(rawname)
                rhs_clean = stripcomments(swappedrhs).strip() if swappedrhs else ""
                is_reassigned_differently = any(
                    nameti < ati < scopeendti and stripcomments(atext).strip() != newname
                    for (ati, atext) in assigns.get(oldname, [])
                )
                shadow = bool(
                    swappedrhs
                    and startswithname(swappedrhs, newname)
                    and (rhs_clean != newname or is_reassigned_differently)
                )

                chain = scopechainof(nameti)
                seenchain = set(scopeused.get(-1, set()))
                for sid in chain:
                    seenchain |= scopeused.get(sid, set())

                if newname == oldname and not shadow and newname not in seenchain and newname not in keywords:
                    innermost = chain[-1] if chain else -1
                    scopeused.setdefault(innermost, set()).add(oldname)
                    add_rename(oldname, oldname, nameti, after_rhs_ti, scopeendti)
                    continue

                candidate = pick_candidate(newname, oldname, nameti, scopeendti, shadow)
                add_rename(oldname, candidate, nameti, after_rhs_ti, scopeendti)

            ti += 1
            continue

        if tok[0] == "kw" and tok[1] == "function":
            func_scope_end = scopeendfor(ti)
            p_open = next_noncomment(tokens, ti, n)
            while p_open < n and tokens[p_open][0] in ("ident", "op") and tokens[p_open][1] != "(":
                p_open = next_noncomment(tokens, p_open, n)

            if p_open < n and tokens[p_open][0] == "op" and tokens[p_open][1] == "(":
                sig_hints = None
                pk1 = prev_noncomment(tokens, ti)
                if pk1 >= 0 and tokens[pk1][0] == "op" and tokens[pk1][1] == "(":
                    pk2 = prev_noncomment(tokens, pk1)
                    if pk2 >= 0 and tokens[pk2][0] == "ident" and tokens[pk2][1] in ("Connect", "Once", "ConnectParallel"):
                        pk3 = prev_noncomment(tokens, pk2)
                        if pk3 >= 0 and tokens[pk3][0] == "op" and tokens[pk3][1] in ".:":
                            pk4 = prev_noncomment(tokens, pk3)
                            if pk4 >= 0 and tokens[pk4][0] == "ident":
                                sig_tok_name = tokens[pk4][1]
                                resolved_sig = make_resolver(pk4)(sig_tok_name) or sig_tok_name
                                base_sig = re.sub(r"_?\d+$", "", resolved_sig).lower()
                                sig_hints = signalparams.get(base_sig) or signalparams.get(sig_tok_name.lower())

                params = []
                k = next_noncomment(tokens, p_open, n)
                while k < n:
                    pt = tokens[k]
                    if pt[0] == "op" and pt[1] == ")":
                        k += 1
                        break
                    if pt[0] == "op" and pt[1] == ".":
                        k = next_noncomment(tokens, k, n)
                        continue
                    if pt[0] == "ident":
                        p_ti = k
                        p_name = pt[1]
                        p_type = None
                        k = next_noncomment(tokens, k, n)
                        if k < n and tokens[k][0] == "op" and tokens[k][1] == ":":
                            p_type, k = skip_type_annotation(tokens, k, n)
                        params.append((p_ti, p_name, p_type))
                        if k < n and tokens[k][0] == "op" and tokens[k][1] == ",":
                            k = next_noncomment(tokens, k, n)
                            continue
                    else:
                        k += 1

                body_start_ti = k
                for p_idx, (p_ti, p_name, p_type) in enumerate(params):
                    if p_name == "_":
                        continue
                    if isplaceholder(p_name):
                        raw_p = None
                        if sig_hints and p_idx < len(sig_hints):
                            raw_p = sig_hints[p_idx]
                        if not raw_p and p_type:
                            raw_p = safeident(p_type)
                        if not raw_p:
                            raw_p = infer_param_from_usage(tokens, code, p_name, body_start_ti, func_scope_end, n)
                        new_p = tocamel(raw_p)
                        cand_p = pick_candidate(new_p, p_name, p_ti, func_scope_end, False)
                        add_rename(p_name, cand_p, p_ti, p_ti, func_scope_end)
                    else:
                        chain = scopechainof(p_ti)
                        innermost = chain[-1] if chain else -1
                        scopeused.setdefault(innermost, set()).add(p_name)
                        add_rename(p_name, p_name, p_ti, p_ti, func_scope_end)

            ti += 1
            continue

        if tok[0] == "kw" and tok[1] == "for":
            loop_scope_end = scopeendfor(ti)
            loop_vars = []
            k = next_noncomment(tokens, ti, n)
            while k < n:
                lt = tokens[k]
                if lt[0] == "ident":
                    l_ti = k
                    l_name = lt[1]
                    l_type = None
                    k = next_noncomment(tokens, k, n)
                    if k < n and tokens[k][0] == "op" and tokens[k][1] == ":":
                        l_type, k = skip_type_annotation(tokens, k, n)
                    loop_vars.append((l_ti, l_name, l_type))
                    if k < n and tokens[k][0] == "op" and tokens[k][1] == ",":
                        k = next_noncomment(tokens, k, n)
                        continue
                    break
                else:
                    break

            if loop_vars and k < n:
                sep_tok = tokens[k]
                do_ti = k + 1
                p_depth = 0
                while do_ti < n:
                    dtok = tokens[do_ti]
                    if dtok[0] == "op":
                        if dtok[1] in "([{":
                            p_depth += 1
                        elif dtok[1] in ")]}" and p_depth > 0:
                            p_depth -= 1
                    elif dtok[0] == "kw" and dtok[1] == "do" and p_depth == 0:
                        break
                    do_ti += 1

                if sep_tok[0] == "op" and sep_tok[1] == "=":
                    l_ti, l_name, l_type = loop_vars[0]
                    if isplaceholder(l_name):
                        cand = pick_candidate("index", l_name, l_ti, loop_scope_end, False)
                        add_rename(l_name, cand, l_ti, do_ti, loop_scope_end)
                    else:
                        chain = scopechainof(l_ti)
                        innermost = chain[-1] if chain else -1
                        scopeused.setdefault(innermost, set()).add(l_name)
                        add_rename(l_name, l_name, l_ti, do_ti, loop_scope_end)

                elif sep_tok[0] == "kw" and sep_tok[1] == "in":
                    iter_start_pos = sep_tok[3]
                    iter_end_pos = tokens[do_ti][2] if do_ti < n else len(code)
                    iter_raw = code[iter_start_pos:iter_end_pos].strip()
                    iter_swapped = applymap(iter_raw, make_resolver(k))

                    is_ipairs = bool(re.match(r"^ipairs\s*\(", iter_swapped))
                    coll_expr = iter_swapped
                    m_iter = re.match(r"^(?:ipairs|pairs)\s*\((.+)\)\s*$", iter_swapped, re.DOTALL)
                    if m_iter:
                        coll_expr = m_iter.group(1).strip()
                    else:
                        m_next = re.match(r"^next\s*,\s*(.+)$", iter_swapped, re.DOTALL)
                        if m_next:
                            coll_expr = m_next.group(1).strip()

                    coll_inferred = infername(coll_expr)
                    val_raw = singularize_indexed(coll_inferred) if coll_inferred else "Value"
                    if val_raw == coll_inferred and coll_inferred:
                        m_tag = re.search(r'GetTagged\s*\(\s*["\']([^"\']+)["\']', coll_expr)
                        if m_tag:
                            val_raw = normalizeclassname(m_tag.group(1))
                        elif val_raw not in singularmap.values():
                            val_raw = "Value"

                    for l_idx, (l_ti, l_name, l_type) in enumerate(loop_vars):
                        if l_name == "_":
                            continue
                        if isplaceholder(l_name):
                            if l_type and safeident(l_type):
                                raw_l = safeident(l_type)
                            elif l_idx == 0:
                                raw_l = "Index" if is_ipairs else "Key"
                            elif l_idx == 1:
                                raw_l = val_raw or "Value"
                            else:
                                raw_l = f"Value{l_idx}"
                            new_l = tocamel(raw_l)
                            cand_l = pick_candidate(new_l, l_name, l_ti, loop_scope_end, False)
                            add_rename(l_name, cand_l, l_ti, do_ti, loop_scope_end)
                        else:
                            chain = scopechainof(l_ti)
                            innermost = chain[-1] if chain else -1
                            scopeused.setdefault(innermost, set()).add(l_name)
                            add_rename(l_name, l_name, l_ti, do_ti, loop_scope_end)

            ti += 1
            continue

        ti += 1

    covered_names = {}
    for oldname, newname, declti, activeti, scopeendti in renames:
        covered_names.setdefault(oldname, []).append((declti, scopeendti))

    for oldname, assign_list in assigns.items():
        if not isplaceholder(oldname):
            continue
        for (ati, atext) in assign_list:
            if any(dt <= ati < et for dt, et in covered_names.get(oldname, [])):
                continue
            swapped = applymap(atext, make_resolver(ati))
            rawname = infername(swapped)
            if rawname:
                newname = tocamel(rawname)
                cand = pick_candidate(newname, oldname, ati, n, False)
                add_rename(oldname, cand, ati, ati, n)
                covered_names.setdefault(oldname, []).append((0, n))
                break

    if not renames:
        return code

    byname = {}
    for oldname, newname, declti, activeti, scopeendti in renames:
        byname.setdefault(oldname, []).append((newname, declti, activeti, scopeendti))

    ops = []
    for ti, tok in enumerate(tokens):
        if tok[0] != "ident":
            continue
        if ti in table_keys or is_dot_or_colon_access(tokens, ti):
            continue
        rules = byname.get(tok[1])
        if not rules:
            continue
        bestname = None
        bestdecl = -1
        for newname, declti, activeti, scopeendti in rules:
            if (ti == declti or (activeti <= ti < scopeendti)) and declti > bestdecl:
                bestname = newname
                bestdecl = declti
        if bestname is not None and bestname != tok[1]:
            ops.append((tok[2], tok[3], bestname))

    if not ops:
        return code

    ops.sort()
    out = []
    last = 0
    for start, end, newtext in ops:
        if start < last:
            continue
        out.append(code[last:start])
        out.append(newtext)
        last = end
    out.append(code[last:])
    return "".join(out)


def portfree(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False


def anyport(host, low=20000, high=65000, tries=200):
    for _ in range(tries):
        port = random.randint(low, high)
        if portfree(host, port):
            return port
    for port in range(low, high):
        if portfree(host, port):
            return port
    return None


html = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luau Renamer</title>
<style>
  :root, [data-theme="dark"] {
    --bg: #050505;
    --bg-grad: radial-gradient(circle at 18% 12%, #141416 0%, #060607 52%, #020203 100%);
    --surface: rgba(14, 14, 16, 0.56);
    --editor: rgba(6, 6, 8, 0.52);
    --border: rgba(255, 255, 255, 0.09);
    --border-focus: rgba(255, 255, 255, 0.22);
    --text: #d4d4d4;
    --text-dim: #737373;
    --accent: #e5e5e5;
    --accent-fg: #050505;
    --btn-bg: rgba(255, 255, 255, 0.05);
    --btn-hover: rgba(255, 255, 255, 0.11);
    --select-bg: #0b0b0b;
    --glass-shadow: 0 10px 32px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    --ok: #4ade80;
    --err: #ef4444;
  }
  [data-theme="gruvbox"] {
    --bg: #1d2021;
    --bg-grad: radial-gradient(circle at 18% 12%, #2b2827 0%, #1d2021 55%, #141617 100%);
    --surface: rgba(40, 40, 40, 0.56);
    --editor: rgba(24, 26, 27, 0.52);
    --border: rgba(235, 219, 178, 0.12);
    --border-focus: rgba(254, 128, 25, 0.42);
    --text: #ebdbb2;
    --text-dim: #928374;
    --accent: #fe8019;
    --accent-fg: #1d2021;
    --btn-bg: rgba(235, 219, 178, 0.06);
    --btn-hover: rgba(235, 219, 178, 0.12);
    --select-bg: #282828;
    --glass-shadow: 0 10px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(235, 219, 178, 0.06);
    --ok: #b8bb26;
    --err: #fb4934;
  }
  [data-theme="light"] {
    --bg: #e4e4e7;
    --bg-grad: radial-gradient(circle at 18% 12%, #fafafa 0%, #e4e4e7 60%, #d4d4d8 100%);
    --surface: rgba(255, 255, 255, 0.58);
    --editor: rgba(255, 255, 255, 0.50);
    --border: rgba(24, 24, 27, 0.12);
    --border-focus: rgba(24, 24, 27, 0.28);
    --text: #18181b;
    --text-dim: #71717a;
    --accent: #18181b;
    --accent-fg: #ffffff;
    --btn-bg: rgba(24, 24, 27, 0.05);
    --btn-hover: rgba(24, 24, 27, 0.10);
    --select-bg: #ffffff;
    --glass-shadow: 0 10px 30px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.7);
    --ok: #059669;
    --err: #dc2626;
  }
  * { box-sizing: border-box; }
  html { min-height: 100%; }
  body {
    min-height: 100vh;
    margin: 0;
    padding: 20px;
    font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace;
    color: var(--text);
    background-color: var(--bg);
    background-image: var(--bg-grad);
    background-attachment: fixed;
    font-size: 13px;
    display: flex;
    flex-direction: column;
  }
  .wrap {
    width: 100%;
    max-width: 1600px;
    min-height: calc(100vh - 40px);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    flex: 1 0 auto;
    gap: 14px;
  }
  .top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: var(--surface);
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: var(--glass-shadow);
    flex-shrink: 0;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  h1 {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  .hint {
    font-size: 11px;
    color: var(--text-dim);
  }
  .controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .theme-pick {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: var(--btn-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
  }
  .theme-pick label {
    font-size: 11px;
    color: var(--text-dim);
  }
  select {
    background: transparent;
    color: var(--text);
    border: none;
    font-size: 12px;
    font-family: inherit;
    cursor: pointer;
    outline: none;
  }
  select option {
    background: var(--select-bg);
    color: var(--text);
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    flex: 1 0 auto;
  }
  .pane {
    display: flex;
    flex-direction: column;
    min-height: 580px;
    background: var(--surface);
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    box-shadow: var(--glass-shadow);
  }
  .pane-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    gap: 8px;
    flex-shrink: 0;
  }
  .pane-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-dim);
    font-weight: 600;
  }
  textarea {
    flex: 1 0 auto;
    width: 100%;
    min-height: 500px;
    padding: 14px;
    background: var(--editor);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: inherit;
    font-size: 13px;
    line-height: 1.55;
    resize: vertical;
    outline: none;
    tab-size: 4;
  }
  textarea:focus {
    border-color: var(--border-focus);
  }
  textarea::placeholder {
    color: var(--text-dim);
    opacity: 0.7;
  }
  .toolbar {
    display: flex;
    gap: 6px;
  }
  button {
    background: var(--btn-bg);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  button:hover:not(:disabled) {
    background: var(--btn-hover);
    border-color: var(--border-focus);
  }
  button:active:not(:disabled) {
    transform: translateY(1px);
  }
  button.primary {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--accent-fg);
    font-weight: 600;
    padding: 7px 20px;
  }
  button.primary:hover:not(:disabled) {
    opacity: 0.9;
    background: var(--accent);
  }
  button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .bottom-bar {
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 12px 16px;
    background: var(--surface);
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: var(--glass-shadow);
    flex-shrink: 0;
  }
  .status {
    color: var(--text-dim);
    font-size: 12px;
    margin-left: auto;
  }
  .status.ok { color: var(--ok); }
  .status.err { color: var(--err); }
  input[type=file] { display: none; }
  @media (max-width: 760px) {
    .grid { grid-template-columns: 1fr; }
    .pane { min-height: 380px; }
    textarea { min-height: 310px; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="brand">
        <h1>Luau Renamer</h1>
        <span class="hint">Ctrl+Enter to rename</span>
      </div>
      <div class="controls">
        <div class="theme-pick">
          <label for="theme">Theme</label>
          <select id="theme">
            <option value="dark">Dark</option>
            <option value="gruvbox">Gruvbox</option>
            <option value="light">Light</option>
          </select>
        </div>
      </div>
    </div>
    <div class="grid">
      <div class="pane in">
        <div class="pane-header">
          <span class="pane-title">Input</span>
          <div class="toolbar">
            <button id="uploadbtn">Upload</button>
            <button id="clearinput">Clear</button>
          </div>
        </div>
        <textarea id="input" placeholder="Paste Luau code here..." spellcheck="false"></textarea>
        <input type="file" id="fileinput">
      </div>
      <div class="pane out">
        <div class="pane-header">
          <span class="pane-title">Output</span>
          <div class="toolbar">
            <button id="copybtn" disabled>Copy</button>
            <button id="downloadbtn" disabled>Download</button>
          </div>
        </div>
        <textarea id="output" placeholder="Renamed output..." readonly spellcheck="false"></textarea>
      </div>
    </div>
    <div class="bottom-bar">
      <button class="primary" id="renamebtn">Rename</button>
      <span class="status" id="status"></span>
    </div>
  </div>
<script>
const $ = (id) => document.getElementById(id);

function setstatus(msg, cls) {
  const s = $("status");
  s.textContent = msg;
  s.className = "status" + (cls ? " " + cls : "");
}

let stored = localStorage.getItem("luaurenamer-theme");
if (stored === "carbon") stored = "dark";
if (stored && ["dark", "gruvbox", "light"].includes(stored)) {
  document.documentElement.setAttribute("data-theme", stored);
  $("theme").value = stored;
}
$("theme").onchange = (e) => {
  const t = e.target.value;
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem("luaurenamer-theme", t);
};

$("uploadbtn").onclick = () => $("fileinput").click();
$("fileinput").onchange = (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    $("input").value = r.result;
    setstatus("Loaded " + f.name + " (" + f.size + " B)", "ok");
  };
  r.readAsText(f);
  e.target.value = "";
};

$("clearinput").onclick = () => {
  $("input").value = "";
  $("output").value = "";
  $("copybtn").disabled = true;
  $("downloadbtn").disabled = true;
  setstatus("");
};

/*__TABLES__*/
const RE_SPLIT_CLASS = /[\s_\-]+/;
const RE_VALID_IDENT_FULL = /^[A-Za-z_]\w*$/;
const RE_VALID_IDENT_AT = /[A-Za-z_]\w*/y;
const RE_PLACEHOLDER_1 = /^[a-zA-Z]{1,3}\d+[a-zA-Z0-9_]*$/;
const RE_PLACEHOLDER_2 = /^_*(?:[a-zA-Z]_[a-zA-Z]_?\d+|[a-zA-Z]\d*_\d+|(?:var|arg|upval|func|tbl|tmp|local|param|reg|slot|const|idx|val)_?\d+)$/;
const RE_URL = /https?:\/\/([^\s"'`<>\)\]]+)/i;
const RE_URL_EXT = /\.(?:luau|lua|txt|json|min|js)+$/i;
const RE_NON_ALNUM = /[^A-Za-z0-9_\-]/g;
const RE_VER_NUM = /^v?\d+(?:\.\d+)*$/i;

function normalizeclassname(name) {
  return name.split(RE_SPLIT_CLASS).filter(Boolean).map(p => p[0].toUpperCase() + p.slice(1)).join("");
}

function isvalididentifier(s) {
  return RE_VALID_IDENT_FULL.test(s);
}

function safeident(n) {
  if (!n || !isvalididentifier(n)) return null;
  if (keywords.has(n.toLowerCase())) return null;
  return n;
}

function isplaceholder(name) {
  if (!name || name === "_") return false;
  return RE_PLACEHOLDER_1.test(name) || RE_PLACEHOLDER_2.test(name);
}

function tocamel(name) {
  if (!name) return name;
  return name[0].toLowerCase() + name.slice(1);
}

function joinsuffix(base, num) {
  if (base && /\d$/.test(base)) return base + "_" + num;
  return base + num;
}

function infer_from_url(text) {
  const m = RE_URL.exec(text);
  if (!m) return null;
  const url_body = m[1].split("?")[0].split("#")[0].replace(/[\/.,;:!)\]}"']+$/, "");
  const slashIdx = url_body.indexOf("/");
  if (slashIdx === -1) return null;
  const host = url_body.slice(0, slashIdx);
  const path = url_body.slice(slashIdx + 1);
  const raw_segs = path.split("/").filter(Boolean);
  if (!raw_segs.length) return null;

  const cleaned = [];
  for (let s of raw_segs) {
    s = s.replace(RE_URL_EXT, "").replace(RE_NON_ALNUM, "");
    if (s) cleaned.push(s);
  }
  if (!cleaned.length) return null;

  const host_l = host.toLowerCase();
  const is_git_host = ["github", "githubusercontent", "gitlab", "bitbucket"].some(h => host_l.includes(h));
  if (is_git_host && cleaned.length >= 2) {
    for (let i = cleaned.length - 1; i >= 2; i--) {
      const seg = cleaned[i];
      const sl = seg.toLowerCase();
      if (!GENERIC_URL_SEGMENTS.has(sl) && !/^\d+$/.test(seg) && !RE_VER_NUM.test(sl)) {
        return safeident(normalizeclassname(seg));
      }
    }
    const repo = cleaned[1];
    if (!GENERIC_URL_SEGMENTS.has(repo.toLowerCase()) && !/^\d+$/.test(repo)) {
      return safeident(normalizeclassname(repo));
    }
    const owner = cleaned[0];
    if (!GENERIC_URL_SEGMENTS.has(owner.toLowerCase()) && !/^\d+$/.test(owner)) {
      return safeident(normalizeclassname(owner));
    }
  }

  for (let i = cleaned.length - 1; i >= 0; i--) {
    const seg = cleaned[i];
    const sl = seg.toLowerCase();
    if (!GENERIC_URL_SEGMENTS.has(sl) && !/^\d+$/.test(seg) && !RE_VER_NUM.test(sl)) {
      return safeident(normalizeclassname(seg));
    }
  }
  return null;
}

function readlongbracket(text, i) {
  const n = text.length;
  if (i + 1 >= n || text[i] !== "[") return -1;
  let j = i + 1;
  let eq = 0;
  while (j < n && text[j] === "=") { eq++; j++; }
  if (j < n && text[j] === "[") {
    const close = "]" + "=".repeat(eq) + "]";
    const end = text.indexOf(close, j + 1);
    return end === -1 ? n : end + close.length;
  }
  return -1;
}

function scanbacktick(text, start) {
  let i = start + 1;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (c === "\\") { i += 2; continue; }
    if (c === "`") return ["done", i + 1];
    if (c === "{") return ["interp", i + 1];
    i++;
  }
  return ["done", n];
}

function stripcomments(text) {
  const out = [];
  let i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (c === '"' || c === "'" || c === "`") {
      const q = c;
      const start = i++;
      while (i < n && text[i] !== q) {
        if (text[i] === "\\" && i + 1 < n) i += 2;
        else if (q !== "`" && text[i] === "\n") break;
        else i++;
      }
      if (i < n && text[i] === q) i++;
      out.push(text.slice(start, i));
      continue;
    }
    if (c === "-" && i + 1 < n && text[i + 1] === "-") {
      const lb = readlongbracket(text, i + 2);
      if (lb !== -1) i = lb;
      else {
        const j = text.indexOf("\n", i);
        i = j === -1 ? n : j;
      }
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(text, i);
      if (lb !== -1) {
        out.push(text.slice(i, lb));
        i = lb;
        continue;
      }
    }
    out.push(c);
    i++;
  }
  return out.join("");
}

function startswithname(text, name) {
  if (!text || !name) return false;
  text = stripcomments(text);
  const stripped = text.replace(/"(?:\\.|[^"\\\n])*"/g, '""').replace(/'(?:\\.|[^'\\\n])*'/g, "''");
  const m = /^\s*([A-Za-z_]\w*)/.exec(stripped);
  return Boolean(m && m[1] === name);
}

function isAlpha(c) {
  const code = c.charCodeAt(0);
  return (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
}

function isDigit(c) {
  const code = c.charCodeAt(0);
  return code >= 48 && code <= 57;
}

function isAlnum(c) {
  return isAlpha(c) || isDigit(c);
}

function readstmt(code, start) {
  let i = start;
  const n = code.length;
  let depth = 0;
  let blockdepth = 0;
  let exprifdepth = 0;
  let awaitingdo = false;
  let prev_word_or_op = "=";
  while (i < n) {
    const c = code[i];
    if (c === " " || c === "\t" || c === "\r") { i++; continue; }
    if (c === '"' || c === "'" || c === "`") {
      const q = c;
      i++;
      while (i < n && code[i] !== q) {
        if (code[i] === "\\" && i + 1 < n) i += 2;
        else if (q !== "`" && code[i] === "\n") break;
        else i++;
      }
      if (i < n && code[i] === q) i++;
      prev_word_or_op = "str";
      continue;
    }
    if (c === "-" && i + 1 < n && code[i + 1] === "-") {
      const lb = readlongbracket(code, i + 2);
      if (lb !== -1) { i = lb; continue; }
      const j = code.indexOf("\n", i);
      if (depth === 0 && blockdepth === 0) return [code.slice(start, i), i];
      i = j === -1 ? n : j;
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(code, i);
      if (lb !== -1) {
        i = lb;
        prev_word_or_op = "str";
        continue;
      }
    }
    if (c === "(" || c === "[" || c === "{") {
      depth++;
      prev_word_or_op = c;
      i++;
      continue;
    }
    if (c === ")" || c === "]" || c === "}") {
      if (depth > 0) {
        depth--;
        prev_word_or_op = c;
        i++;
        continue;
      } else {
        return [code.slice(start, i), i];
      }
    }
    if (c === ";" && depth === 0 && blockdepth === 0) return [code.slice(start, i), i];
    if (c === "\n" && depth === 0 && blockdepth === 0) return [code.slice(start, i), i];
    if (isAlpha(c) || c === "_") {
      const wstart = i;
      while (i < n && (isAlnum(code[i]) || code[i] === "_")) i++;
      const w = code.slice(wstart, i);
      if (depth === 0) {
        if (w === "function") blockdepth++;
        else if (w === "if") {
          if (["=", ",", "(", "[", "{", "return", "and", "or", "not", "elseif", "then", "else", "+", "-", "*", "/", ".."].includes(prev_word_or_op)) {
            exprifdepth++;
          } else {
            if (blockdepth === 0) return [code.slice(start, wstart), wstart];
            blockdepth++;
          }
        } else if (w === "for" || w === "while") {
          if (blockdepth === 0) return [code.slice(start, wstart), wstart];
          awaitingdo = true;
          blockdepth++;
        } else if (w === "do") {
          if (blockdepth === 0) return [code.slice(start, wstart), wstart];
          if (awaitingdo) awaitingdo = false;
          else blockdepth++;
        } else if (w === "repeat") {
          if (blockdepth === 0) return [code.slice(start, wstart), wstart];
          blockdepth++;
        } else if (w === "else") {
          if (exprifdepth > 0 && blockdepth === 0) exprifdepth--;
          else if (blockdepth === 0) return [code.slice(start, wstart), wstart];
        } else if (w === "elseif") {
          if (exprifdepth === 0 && blockdepth === 0) return [code.slice(start, wstart), wstart];
        } else if (w === "end" || w === "until") {
          if (blockdepth > 0) blockdepth--;
          else return [code.slice(start, wstart), wstart];
        } else if ((w === "local" || w === "return" || w === "break" || w === "continue") && blockdepth === 0) {
          return [code.slice(start, wstart), wstart];
        }
      }
      prev_word_or_op = w;
      continue;
    }
    prev_word_or_op = c;
    i++;
  }
  return [code.slice(start, n), n];
}

function splitcommas(text) {
  const parts = [];
  let depth = 0;
  let last = 0;
  let i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (c === '"' || c === "'" || c === "`") {
      const q = c;
      i++;
      while (i < n && text[i] !== q) {
        if (text[i] === "\\" && i + 1 < n) i += 2;
        else if (q !== "`" && text[i] === "\n") break;
        else i++;
      }
      if (i < n && text[i] === q) i++;
      continue;
    }
    if (c === "-" && i + 1 < n && text[i + 1] === "-") {
      const lb = readlongbracket(text, i + 2);
      if (lb !== -1) i = lb;
      else {
        const j = text.indexOf("\n", i);
        i = j === -1 ? n : j;
      }
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(text, i);
      if (lb !== -1) { i = lb; continue; }
    }
    if (c === "(" || c === "[" || c === "{") depth++;
    else if (c === ")" || c === "]" || c === "}") { if (depth > 0) depth--; }
    else if (c === "," && depth === 0) {
      parts.push(text.slice(last, i));
      last = i + 1;
    }
    i++;
  }
  parts.push(text.slice(last));
  return parts;
}

function applymap(text, resolve_fn) {
  if (!resolve_fn) return text;
  const result = [];
  let i = 0;
  const n = text.length;
  const interp_stack = [];
  const brace_stack = [];
  while (i < n) {
    const c = text[i];
    if (c === '"' || c === "'") {
      const start = i;
      const q = c;
      i++;
      while (i < n && text[i] !== q) {
        if (text[i] === "\\" && i + 1 < n) i += 2;
        else if (text[i] === "\n") break;
        else i++;
      }
      if (i < n && text[i] === q) i++;
      result.push(text.slice(start, i));
      continue;
    }
    if (c === "`") {
      const [kind, stop] = scanbacktick(text, i);
      result.push(text.slice(i, stop));
      i = stop;
      if (kind === "interp") interp_stack.push(0);
      continue;
    }
    if (c === "-" && i + 1 < n && text[i + 1] === "-") {
      const lb = readlongbracket(text, i + 2);
      if (lb !== -1) {
        result.push(text.slice(i, lb));
        i = lb;
      } else {
        let j = text.indexOf("\n", i);
        if (j === -1) j = n;
        result.push(text.slice(i, j));
        i = j;
      }
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(text, i);
      if (lb !== -1) {
        result.push(text.slice(i, lb));
        i = lb;
        continue;
      }
    }
    if (c === "{") {
      if (interp_stack.length) interp_stack[interp_stack.length - 1]++;
      brace_stack.push("{");
      result.push(c);
      i++;
      continue;
    }
    if (c === "}") {
      if (brace_stack.length && brace_stack[brace_stack.length - 1] === "{") brace_stack.pop();
      if (interp_stack.length && interp_stack[interp_stack.length - 1] === 0) {
        interp_stack.pop();
        const [kind, stop] = scanbacktick(text, i);
        result.push(text.slice(i, stop));
        i = stop;
        if (kind === "interp") interp_stack.push(0);
        continue;
      } else if (interp_stack.length) {
        interp_stack[interp_stack.length - 1]--;
      }
      result.push(c);
      i++;
      continue;
    }
    if (c === "(" || c === "[") {
      brace_stack.push(c);
      result.push(c);
      i++;
      continue;
    }
    if (c === ")" || c === "]") {
      if (brace_stack.length) brace_stack.pop();
      result.push(c);
      i++;
      continue;
    }
    if (isAlpha(c) || c === "_") {
      RE_VALID_IDENT_AT.lastIndex = i;
      const m = RE_VALID_IDENT_AT.exec(text);
      const word = m[0];
      let k = i - 1;
      while (k >= 0 && " \t\n\r".includes(text[k])) k--;
      const isfield = k >= 0 && (text[k] === "." || text[k] === ":") && !(text[k] === "." && k >= 1 && text[k - 1] === ".");
      let r = i + word.length;
      while (r < n && " \t\n\r".includes(text[r])) r++;
      const istablekey = (
        brace_stack.length && brace_stack[brace_stack.length - 1] === "{" &&
        k >= 0 && "{,;".includes(text[k]) &&
        r < n && text[r] === "=" &&
        (r + 1 >= n || text[r + 1] !== "=")
      );
      if (!isfield && !istablekey) {
        const rep = resolve_fn(word);
        result.push(rep !== null && rep !== undefined ? rep : word);
      } else {
        result.push(word);
      }
      i += word.length;
      continue;
    }
    result.push(c);
    i++;
  }
  return result.join("");
}

function get_top_level_spans(e) {
  const matching_open = new Map();
  const stack = [];
  const top_set = new Set();
  let i = 0;
  const n = e.length;
  while (i < n) {
    const c = e[i];
    if (c === '"' || c === "'" || c === "`") {
      const q = c;
      i++;
      while (i < n && e[i] !== q) {
        if (e[i] === "\\" && i + 1 < n) i += 2;
        else if (q !== "`" && e[i] === "\n") break;
        else i++;
      }
      if (i < n && e[i] === q) i++;
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(e, i);
      if (lb !== -1) { i = lb; continue; }
    }
    if (c === "(" || c === "[" || c === "{") {
      stack.push(i);
      i++;
      continue;
    }
    if (c === ")" || c === "]" || c === "}") {
      if (stack.length) matching_open.set(i, stack.pop());
      i++;
      continue;
    }
    if (!stack.length) top_set.add(i);
    i++;
  }
  return [matching_open, top_set];
}

function split_top_keyword(e, kw, top_set) {
  const re = new RegExp("\\b" + kw + "\\b", "g");
  let m;
  while ((m = re.exec(e)) !== null) {
    if (top_set.has(m.index)) {
      return [e.slice(0, m.index).trim(), e.slice(m.index + kw.length).trim()];
    }
  }
  return null;
}

function split_top_binop(e, top_set) {
  const n = e.length;
  for (let i = 0; i < n; i++) {
    if (top_set.has(i)) {
      if (e.slice(i, i + 2) === ".." && (i + 2 >= n || e[i + 2] !== ".")) {
        return [e.slice(0, i).trim(), e.slice(i + 2).trim()];
      }
      if ("+*/%^".includes(e[i])) {
        return [e.slice(0, i).trim(), e.slice(i + 1).trim()];
      }
      if (e[i] === "-" && i > 0) {
        let k = i - 1;
        while (k >= 0 && " \t\r\n".includes(e[k])) k--;
        if (k >= 0 && (isAlnum(e[k]) || "_)]}\"'`".includes(e[k]))) {
          return [e.slice(0, i).trim(), e.slice(i + 1).trim()];
        }
      }
    }
  }
  return null;
}

function singularize_indexed(name) {
  if (!name) return name;
  const base = name.replace(/_?\d+$/, "");
  if (singularmap[base]) return singularmap[base];
  if (base.endsWith("List") && base.length > 4) return base.slice(0, -4);
  if (base.endsWith("ies") && base.length > 4) return base.slice(0, -3) + "y";
  if (base.endsWith("s") && !base.endsWith("ss") && base.length > 3) return base.slice(0, -1);
  return name;
}

function infername(expr) {
  let e = stripcomments(expr).trim();
  while (e.endsWith(";")) e = e.slice(0, -1).trim();
  if (!e) return null;

  const el = e.toLowerCase();
  if (el.includes("http://") || el.includes("https://")) {
    const url_hint = infer_from_url(e);
    if (url_hint) return url_hint;
  }

  let [matching_open, top_set] = get_top_level_spans(e);

  if (e.startsWith("(") && e.endsWith(")") && matching_open.get(e.length - 1) === 0) {
    return infername(e.slice(1, -1));
  }

  if (/^if\b/.test(e)) {
    const sp_then = split_top_keyword(e.slice(2), "then", get_top_level_spans(e.slice(2))[1]);
    if (sp_then) {
      const after_then = sp_then[1];
      const at_top = get_top_level_spans(after_then)[1];
      const sp_el = split_top_keyword(after_then, "elseif", at_top) || split_top_keyword(after_then, "else", at_top);
      if (sp_el) return infername(sp_el[0]) || infername(sp_el[1]);
    }
  }

  const sp_or = split_top_keyword(e, "or", top_set);
  if (sp_or) {
    const [left_or, right_or] = sp_or;
    const left_top = get_top_level_spans(left_or)[1];
    const sp_and = split_top_keyword(left_or, "and", left_top);
    if (sp_and) {
      const [cond_and, val_and] = sp_and;
      return infername(val_and) || infername(cond_and) || infername(right_or);
    }
    return infername(left_or) || infername(right_or);
  }

  const sp_and = split_top_keyword(e, "and", top_set);
  if (sp_and) {
    return infername(sp_and[1]) || infername(sp_and[0]);
  }

  const sp_bin = split_top_binop(e, top_set);
  if (sp_bin) {
    const [left_b, right_b] = sp_bin;
    if (left_b && right_b) return infername(left_b) || infername(right_b);
  }

  if (e.startsWith("#") || (e.startsWith("-") && !/^\d/.test(e.slice(1)))) {
    return infername(e.slice(1).trim());
  }
  const m_not = /^not\b\s*([\s\S]+)$/.exec(e);
  if (m_not) return infername(m_not[1]);

  if (/^function\s*\(/.test(e)) return "Func";

  let m = /^["']([A-Za-z_][A-Za-z0-9_]*)["']\s*$/.exec(e);
  if (m) return safeident(normalizeclassname(m[1]));

  let had_array_index = false;
  while (e.endsWith("]")) {
    const open_b = matching_open.has(e.length - 1) ? matching_open.get(e.length - 1) : -1;
    if (open_b <= 0) break;
    const inside = e.slice(open_b + 1, -1).trim();
    if (/^["']([A-Za-z_][A-Za-z0-9_]*)["']$/.test(inside)) break;
    e = e.slice(0, open_b).trim();
    had_array_index = true;
    [matching_open, top_set] = get_top_level_spans(e);
  }

  function finalize(res) {
    if (!res) return null;
    if (had_array_index) res = singularize_indexed(res);
    return safeident(res);
  }

  if (e.endsWith(")")) {
    const open_p = matching_open.has(e.length - 1) ? matching_open.get(e.length - 1) : -1;
    if (open_p === 0) return finalize(infername(e.slice(1, -1)));
    if (open_p > 0) {
      const callee = e.slice(0, open_p).trim();
      const args_str = e.slice(open_p + 1, -1).trim();

      if (/(?:^|[.:]\s*)GetService$/.test(callee)) {
        const m_arg = /^["']([^"']+)["']/.exec(args_str);
        if (m_arg) return finalize(normalizeclassname(m_arg[1]));
      }

      if (/^(?:Instance|Drawing)\s*\.\s*new$/.test(callee)) {
        const m_arg = /^["']([^"']+)["']/.exec(args_str);
        if (m_arg) return finalize(normalizeclassname(m_arg[1]));
      }

      const m_find = /[.:]\s*(WaitForChild|FindFirstChild|FindFirstChildOfClass|FindFirstChildWhichIsA)$/.exec(callee);
      if (m_find) {
        const m_arg = /^["']([^"']+)["']/.exec(args_str);
        if (m_arg) {
          let cname = normalizeclassname(m_arg[1]);
          if (keywords.has(cname.toLowerCase())) cname += "Child";
          return finalize(cname);
        }
      }

      const m_dt = /^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)$/.exec(callee);
      if (m_dt) {
        const [, dt, method] = m_dt;
        const n = (method === "new" || method.startsWith("from") || method.startsWith("look") || method === "Angles" || method === "identity")
          ? dt : normalizeclassname(method);
        return finalize(n);
      }

      const m_lib = /^([a-z_]\w*)\s*\.\s*([a-zA-Z_]\w*)$/.exec(callee);
      if (m_lib) {
        const key = `${m_lib[1]}.${m_lib[2]}`;
        if (libmethods[key]) return finalize(libmethods[key]);
        if (globalfunctions[m_lib[2]]) return finalize(globalfunctions[m_lib[2]]);
        return finalize(normalizeclassname(m_lib[2]));
      }

      const m_fn = /^([A-Za-z_]\w*)$/.exec(callee);
      if (m_fn) {
        const fn = m_fn[1];
        return finalize(globalfunctions[fn] || fn);
      }

      const m_meth = /[.:]\s*([A-Za-z_]\w*)$/.exec(callee);
      if (m_meth) {
        const method = m_meth[1];
        if (method === "Wait") {
          if (/CharacterAdded\s*:\s*Wait$/.test(callee)) return finalize("Character");
          if (/PlayerAdded\s*:\s*Wait$/.test(callee)) return finalize("Player");
          if (/ChildAdded\s*:\s*Wait$/.test(callee)) return finalize("Child");
        }
        return finalize(methodnames[method] || normalizeclassname(method));
      }

      if (callee.endsWith(")")) {
        return finalize(infername(callee));
      }
    }
  }

  m = /^Enum\s*\.\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*$/.exec(e);
  if (m) {
    const [, t, v] = m;
    const n = (v.length <= 1 || keywords.has(v.toLowerCase())) ? (t + v) : v;
    return finalize(n);
  }

  m = /^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*$/.exec(e);
  if (m) return finalize(normalizeclassname(m[2]));

  m = /^([a-z_]\w*)\s*\.\s*([a-zA-Z_]\w*)\s*$/.exec(e);
  if (m) {
    const key = `${m[1]}.${m[2]}`;
    if (libmethods[key]) return finalize(libmethods[key]);
  }

  m = /\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*$/.exec(e);
  if (m) {
    const field = m[1];
    let n = field[0].toUpperCase() + field.slice(1);
    if (keywords.has(n.toLowerCase())) n += "Prop";
    return finalize(n);
  }

  m = /\[\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*\]\s*$/.exec(e);
  if (m) {
    const field = m[1];
    let n = field[0].toUpperCase() + field.slice(1);
    if (keywords.has(n.toLowerCase())) n += "Field";
    return finalize(n);
  }

  m = /^([a-zA-Z_]\w*)\s*$/.exec(e);
  if (m) {
    const name = m[1];
    if (keywords.has(name.toLowerCase())) return null;
    const n = name[0].toUpperCase() + name.slice(1);
    return finalize(n);
  }

  return null;
}

function tokenize(code) {
  const tokens = [];
  let i = 0;
  const n = code.length;
  const interp_stack = [];
  while (i < n) {
    const c = code[i];
    if (c === " " || c === "\t" || c === "\r" || c === "\n") { i++; continue; }
    if (c === "-" && i + 1 < n && code[i + 1] === "-") {
      const start = i;
      const lb = readlongbracket(code, i + 2);
      if (lb !== -1) i = lb;
      else {
        const end = code.indexOf("\n", i);
        i = end === -1 ? n : end;
      }
      tokens.push(["comment", code.slice(start, i), start, i]);
      continue;
    }
    if (c === '"' || c === "'") {
      const start = i;
      const q = c;
      i++;
      while (i < n && code[i] !== q) {
        if (code[i] === "\\" && i + 1 < n) i += 2;
        else if (code[i] === "\n") break;
        else i++;
      }
      if (i < n && code[i] === q) i++;
      tokens.push(["string", code.slice(start, i), start, i]);
      continue;
    }
    if (c === "`") {
      const [kind, stop] = scanbacktick(code, i);
      tokens.push(["string", code.slice(i, stop), i, stop]);
      i = stop;
      if (kind === "interp") interp_stack.push(0);
      continue;
    }
    if (c === "{") {
      if (interp_stack.length) interp_stack[interp_stack.length - 1]++;
      tokens.push(["op", "{", i, i + 1]);
      i++;
      continue;
    }
    if (c === "}") {
      if (interp_stack.length && interp_stack[interp_stack.length - 1] === 0) {
        interp_stack.pop();
        const [kind, stop] = scanbacktick(code, i);
        tokens.push(["string", code.slice(i, stop), i, stop]);
        i = stop;
        if (kind === "interp") interp_stack.push(0);
        continue;
      } else if (interp_stack.length) {
        interp_stack[interp_stack.length - 1]--;
      }
      tokens.push(["op", "}", i, i + 1]);
      i++;
      continue;
    }
    if (c === "[") {
      const lb = readlongbracket(code, i);
      if (lb !== -1) {
        tokens.push(["string", code.slice(i, lb), i, lb]);
        i = lb;
        continue;
      }
    }
    if (isAlpha(c) || c === "_") {
      const start = i;
      while (i < n && (isAlnum(code[i]) || code[i] === "_")) i++;
      const word = code.slice(start, i);
      tokens.push([keywords.has(word) ? "kw" : "ident", word, start, i]);
      continue;
    }
    if (isDigit(c) || (c === "." && i + 1 < n && isDigit(code[i + 1]))) {
      const start = i;
      while (i < n && (isAlnum(code[i]) || code[i] === "." || code[i] === "_")) i++;
      tokens.push(["num", code.slice(start, i), start, i]);
      continue;
    }
    tokens.push(["op", c, i, i + 1]);
    i++;
  }
  return tokens;
}

function prev_noncomment(tokens, ti) {
  let k = ti - 1;
  while (k >= 0 && tokens[k][0] === "comment") k--;
  return k;
}

function next_noncomment(tokens, ti, n) {
  let k = ti + 1;
  while (k < n && tokens[k][0] === "comment") k++;
  return k;
}

function is_dot_or_colon_access(tokens, ti) {
  const pk = prev_noncomment(tokens, ti);
  if (pk < 0) return false;
  const pt = tokens[pk];
  if (pt[0] !== "op" || (pt[1] !== "." && pt[1] !== ":")) return false;
  if (pt[1] === ".") {
    const pk2 = prev_noncomment(tokens, pk);
    if (pk2 >= 0 && tokens[pk2][0] === "op" && tokens[pk2][1] === "." && tokens[pk2][3] === pt[2]) return false;
  }
  return true;
}

function findscopes(tokens, code) {
  const scopes = [];
  const stack = [];
  let awaitingdo = false;
  const n = tokens.length;
  for (let ti = 0; ti < n; ti++) {
    const tok = tokens[ti];
    if (tok[0] !== "kw") continue;
    const w = tok[1];
    if (w === "for" || w === "while") {
      awaitingdo = true;
      stack.push(["loop", ti, ti]);
    } else if (w === "do") {
      if (awaitingdo) awaitingdo = false;
      else stack.push(["do", ti, ti]);
    } else if (w === "function") {
      stack.push(["func", ti, ti]);
    } else if (w === "repeat") {
      stack.push(["repeat", ti, ti]);
    } else if (w === "if") {
      const pk = prev_noncomment(tokens, ti);
      let is_expr_if = false;
      if (pk >= 0) {
        const pt = tokens[pk];
        if (pt[0] === "op" && "=,([]{+-*/%^<>~".includes(pt[1])) is_expr_if = true;
        else if (pt[0] === "kw" && ["return", "and", "or", "not", "elseif", "then", "else", "while", "until", "in"].includes(pt[1])) is_expr_if = true;
      }
      stack.push([is_expr_if ? "expr_if" : "if", ti, ti]);
    } else if (w === "elseif") {
      if (stack.length && stack[stack.length - 1][0] === "if") {
        const [, openti, branchstart] = stack.pop();
        scopes.push([branchstart, ti]);
        stack.push(["if", openti, ti]);
      }
    } else if (w === "else") {
      if (stack.length && stack[stack.length - 1][0] === "expr_if") stack.pop();
      else if (stack.length && stack[stack.length - 1][0] === "if") {
        const [, openti, branchstart] = stack.pop();
        scopes.push([branchstart, ti]);
        stack.push(["if", openti, ti]);
      }
    } else if (w === "end") {
      while (stack.length && stack[stack.length - 1][0] === "expr_if") stack.pop();
      if (stack.length) {
        const [, , branchstart] = stack.pop();
        scopes.push([branchstart, ti]);
      }
    } else if (w === "until") {
      while (stack.length && stack[stack.length - 1][0] === "expr_if") stack.pop();
      if (stack.length) {
        const [, , branchstart] = stack.pop();
        const [, cond_end_pos] = readstmt(code, tok[3]);
        let end_ti = ti + 1;
        while (end_ti < n && tokens[end_ti][2] < cond_end_pos) end_ti++;
        scopes.push([branchstart, end_ti]);
      }
    }
  }
  return scopes;
}

function compute_table_key_tokens(tokens, n) {
  const table_keys = new Set();
  const bracket_stack = [];
  for (let ti = 0; ti < n; ti++) {
    const tok = tokens[ti];
    if (tok[0] === "op") {
      if ("([{".includes(tok[1])) bracket_stack.push(tok[1]);
      else if (")]}".includes(tok[1]) && bracket_stack.length) bracket_stack.pop();
    } else if (tok[0] === "ident") {
      if (bracket_stack.length && bracket_stack[bracket_stack.length - 1] === "{") {
        const pk = prev_noncomment(tokens, ti);
        const nk = next_noncomment(tokens, ti, n);
        if (pk >= 0 && nk < n) {
          const pt = tokens[pk];
          const nt = tokens[nk];
          if (pt[0] === "op" && "{,;".includes(pt[1]) && nt[0] === "op" && nt[1] === "=") {
            const nk2 = next_noncomment(tokens, nk, n);
            if (nk2 >= n || !(tokens[nk2][0] === "op" && tokens[nk2][1] === "=")) {
              table_keys.add(ti);
            }
          }
        }
      }
    }
  }
  return table_keys;
}

function skip_type_annotation(tokens, j, n) {
  let k = next_noncomment(tokens, j, n);
  let depth = 0;
  let type_hint = null;
  while (k < n) {
    const t = tokens[k];
    if (t[0] === "comment") { k++; continue; }
    if (depth === 0) {
      if (t[0] === "op" && ",=;)".includes(t[1])) break;
      if (t[0] === "kw" && !["nil", "true", "false", "function"].includes(t[1])) break;
    }
    if (t[0] === "op") {
      if ("([{<".includes(t[1])) depth++;
      else if (")]}>".includes(t[1])) {
        if (depth > 0) depth--;
        else break;
      }
    } else if (t[0] === "ident" && depth === 0 && type_hint === null) {
      if (!["any", "unknown", "never", "nil"].includes(t[1].toLowerCase())) {
        type_hint = normalizeclassname(t[1]);
      }
    }
    k++;
  }
  return [type_hint, k];
}

function collectassigns(tokens, code, n, table_keys) {
  const assigns = new Map();
  let ti = 0;
  while (ti < n - 1) {
    const tok = tokens[ti];
    if (tok[0] === "kw" && tok[1] === "local") {
      let j = next_noncomment(tokens, ti, n);
      while (j < n) {
        const t = tokens[j];
        if (t[0] === "ident") {
          j = next_noncomment(tokens, j, n);
          if (j < n && tokens[j][0] === "op" && tokens[j][1] === ":") {
            [, j] = skip_type_annotation(tokens, j, n);
          }
          if (j < n && tokens[j][0] === "op" && tokens[j][1] === ",") {
            j = next_noncomment(tokens, j, n);
            continue;
          }
          break;
        } else break;
      }
      ti = j + 1;
      continue;
    }
    if (tok[0] !== "ident" || table_keys.has(ti) || is_dot_or_colon_access(tokens, ti)) {
      ti++;
      continue;
    }
    const nk = next_noncomment(tokens, ti, n);
    if (nk >= n) break;
    const op1 = tokens[nk];
    if (op1[0] !== "op" || op1[1] !== "=") { ti++; continue; }
    const nk2 = next_noncomment(tokens, nk, n);
    if (nk2 < n && tokens[nk2][0] === "op" && tokens[nk2][1] === "=") {
      ti = nk2 + 1;
      continue;
    }
    const pk = prev_noncomment(tokens, ti);
    if (pk >= 0) {
      const prev = tokens[pk];
      if (prev[0] === "kw" && (prev[1] === "for" || prev[1] === "local")) { ti++; continue; }
      if (prev[0] === "op" && "~<>".includes(prev[1])) { ti++; continue; }
    }
    const rhsstart = op1[3];
    const [rhstext] = readstmt(code, rhsstart);
    if (!assigns.has(tok[1])) assigns.set(tok[1], []);
    assigns.get(tok[1]).push([ti, rhstext]);
    ti = nk + 1;
  }
  return assigns;
}

function infer_multireturn(rhs_expr, idx) {
  const e = stripcomments(rhs_expr).trim();
  if (/^(?:pcall|xpcall)\s*\(/.test(e)) {
    if (idx === 1) {
      const m_ret = /\breturn\s+([\s\S]+?)\s+end\s*[,)]/.exec(e);
      if (m_ret) {
        const cand = infername(m_ret[1]);
        if (cand) return cand;
      }
      return "Result";
    }
    return "Result" + idx;
  }
  if (/:\s*GetBoundingBox\s*\(\s*\)$/.test(e) && idx === 1) return "Size";
  if (/^string\s*\.\s*find\s*\(/.test(e)) {
    if (idx === 1) return "EndIndex";
    if (idx >= 2) return "Capture";
  }
  if (/^Color3\s*\.\s*toHSV\s*\(/.test(e)) {
    if (idx === 1) return "Saturation";
    if (idx === 2) return "Value";
  }
  return infername(e);
}

const PLAYER_MEMBERS = new Set([
  "Character", "UserId", "DisplayName", "AccountAge", "Team", "TeamColor",
  "PlayerGui", "Backpack", "PlayerScripts", "StarterGear", "GetMouse", "Kick",
  "GetRankInGroup", "GetRoleInGroup", "IsInGroup", "IsFriendsWith", "LoadCharacter"
]);
const HUMANOID_MEMBERS = new Set([
  "Health", "MaxHealth", "WalkSpeed", "JumpPower", "JumpHeight", "HipHeight",
  "TakeDamage", "ChangeState", "GetState", "LoadAnimation", "EquipTool", "UnequipTools"
]);
const INPUT_MEMBERS = new Set(["KeyCode", "UserInputType", "UserInputState", "Delta"]);
const PART_MEMBERS = new Set([
  "CFrame", "Anchored", "CanCollide", "Transparency", "BrickColor", "Material",
  "AssemblyLinearVelocity", "AssemblyAngularVelocity", "ApplyImpulse"
]);
const INST_MEMBERS = new Set([
  "Parent", "ClassName", "GetChildren", "GetDescendants", "FindFirstChild",
  "WaitForChild", "Destroy", "Clone", "GetAttribute", "SetAttribute"
]);

function infer_param_from_usage(tokens, code, param_name, body_start_ti, body_end_ti, n) {
  const limit = Math.min(body_end_ti, n);
  for (let ti = body_start_ti; ti < limit; ti++) {
    const tok = tokens[ti];
    if (tok[0] !== "ident" || tok[1] !== param_name) continue;
    if (is_dot_or_colon_access(tokens, ti)) continue;
    const nk = next_noncomment(tokens, ti, n);
    if (nk < n && tokens[nk][0] === "op" && (tokens[nk][1] === "." || tokens[nk][1] === ":")) {
      const nk2 = next_noncomment(tokens, nk, n);
      if (nk2 < n && tokens[nk2][0] === "ident") {
        const mem = tokens[nk2][1];
        if (mem === "WaitForChild" || mem === "FindFirstChild") {
          const nk3 = next_noncomment(tokens, nk2, n);
          if (nk3 < n && tokens[nk3][0] === "op" && tokens[nk3][1] === "(") {
            const nk4 = next_noncomment(tokens, nk3, n);
            if (nk4 < n && tokens[nk4][0] === "string") {
              const sval = tokens[nk4][1].replace(/^["'`]|["'`]$/g, "");
              if (["Humanoid", "HumanoidRootPart", "Head", "Torso", "UpperTorso"].includes(sval)) return "Character";
              if (["PlayerGui", "Backpack", "PlayerScripts", "StarterGear"].includes(sval)) return "Player";
            }
          }
        }
        if (mem === "IsA") {
          const nk3 = next_noncomment(tokens, nk2, n);
          if (nk3 < n && tokens[nk3][0] === "op" && tokens[nk3][1] === "(") {
            const nk4 = next_noncomment(tokens, nk3, n);
            if (nk4 < n && tokens[nk4][0] === "string") {
              const sval = tokens[nk4][1].replace(/^["'`]|["'`]$/g, "");
              const cname = normalizeclassname(sval);
              if (safeident(cname)) return cname;
            }
          }
        }
        if (PLAYER_MEMBERS.has(mem)) return "Player";
        if (HUMANOID_MEMBERS.has(mem)) return "Humanoid";
        if (INPUT_MEMBERS.has(mem)) return "Input";
        if (PART_MEMBERS.has(mem)) return "Part";
        if (INST_MEMBERS.has(mem)) return "Inst";
      }
    } else if (nk < n && tokens[nk][0] === "op" && tokens[nk][1] === "(") {
      return "Callback";
    } else if (nk < n && tokens[nk][0] === "op" && "+-*/%^".includes(tokens[nk][1])) {
      return "Num";
    }
  }
  return "Arg";
}

function renamecode(code) {
  const tokens = tokenize(code);
  const n = tokens.length;
  if (n === 0) return code;

  const scopes = findscopes(tokens, code);
  scopes.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const scopestarts = scopes.map(s => s[0]);

  function bisect_right(arr, x) {
    let lo = 0, hi = arr.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (x < arr[mid]) hi = mid;
      else lo = mid + 1;
    }
    return lo;
  }

  function scopeendfor(ti) {
    let pos = bisect_right(scopestarts, ti) - 1;
    while (pos >= 0) {
      const [s, e] = scopes[pos];
      if (e > ti) return e;
      pos--;
    }
    return n;
  }

  function scopechainof(ti) {
    const chain = [];
    for (let sid = 0; sid < scopes.length; sid++) {
      const [s, e] = scopes[sid];
      if (s <= ti && ti < e) chain.push(sid);
    }
    chain.sort((a, b) => scopes[a][0] - scopes[b][0]);
    return chain;
  }

  const table_keys = compute_table_key_tokens(tokens, n);
  const assigns = collectassigns(tokens, code, n, table_keys);

  const declared_vars = [];
  for (let ti_scan = 0; ti_scan < n; ti_scan++) {
    const tok_scan = tokens[ti_scan];
    if (tok_scan[0] === "kw" && tok_scan[1] === "local") {
      let j = next_noncomment(tokens, ti_scan, n);
      if (j < n && tokens[j][0] === "kw" && tokens[j][1] === "function") {
        const fn_ti = next_noncomment(tokens, j, n);
        if (fn_ti < n && tokens[fn_ti][0] === "ident") {
          if (!isplaceholder(tokens[fn_ti][1])) {
            declared_vars.push([tokens[fn_ti][1], fn_ti, scopeendfor(ti_scan)]);
          }
        }
      } else {
        while (j < n) {
          if (tokens[j][0] === "ident") {
            if (!isplaceholder(tokens[j][1])) {
              declared_vars.push([tokens[j][1], j, scopeendfor(ti_scan)]);
            }
            j = next_noncomment(tokens, j, n);
            if (j < n && tokens[j][0] === "op" && tokens[j][1] === ":") {
              [, j] = skip_type_annotation(tokens, j, n);
            }
            if (j < n && tokens[j][0] === "op" && tokens[j][1] === ",") {
              j = next_noncomment(tokens, j, n);
              continue;
            }
          }
          break;
        }
      }
    }
  }

  const scopeused = new Map();
  const renames = [];
  const renames_by_old = new Map();

  function add_used(sid, name) {
    if (!scopeused.has(sid)) scopeused.set(sid, new Set());
    scopeused.get(sid).add(name);
  }

  function add_rename(oldname, newname, declti, activeti, scopeendti) {
    const rule = [oldname, newname, declti, activeti, scopeendti];
    renames.push(rule);
    if (!renames_by_old.has(oldname)) renames_by_old.set(oldname, []);
    renames_by_old.get(oldname).push(rule);
  }

  function make_resolver(at_ti) {
    return function(word) {
      const rules = renames_by_old.get(word);
      if (!rules) return null;
      for (let i = rules.length - 1; i >= 0; i--) {
        const [, nn, , act, et] = rules[i];
        if (act <= at_ti && at_ti < et) return nn;
      }
      return null;
    };
  }

  function get_seenchain(chain) {
    const seen = new Set(scopeused.get(-1) || []);
    for (const sid of chain) {
      const sset = scopeused.get(sid);
      if (sset) for (const v of sset) seen.add(v);
    }
    return seen;
  }

  function pick_candidate(newname, oldname, nameti, scopeendti, shadow) {
    const chain = scopechainof(nameti);
    const seenchain = get_seenchain(chain);
    for (const [decl_name, d_ti, d_end] of declared_vars) {
      if (d_ti !== nameti && decl_name !== oldname && !(d_end <= nameti || d_ti >= scopeendti)) {
        seenchain.add(decl_name);
      }
    }
    let candidate, suffix;
    if (shadow || keywords.has(newname)) {
      candidate = joinsuffix(newname, 2);
      suffix = 3;
    } else {
      candidate = newname;
      suffix = 2;
    }
    while (seenchain.has(candidate) || keywords.has(candidate) || (candidate === oldname && shadow)) {
      candidate = joinsuffix(newname, suffix);
      suffix++;
    }
    const innermost = chain.length ? chain[chain.length - 1] : -1;
    add_used(innermost, candidate);
    return candidate;
  }

  const singular_values = new Set(Object.values(singularmap));

  let ti = 0;
  while (ti < n) {
    const tok = tokens[ti];

    if (tok[0] === "kw" && tok[1] === "local") {
      let j = next_noncomment(tokens, ti, n);

      if (j < n && tokens[j][0] === "kw" && tokens[j][1] === "function") {
        const fn_ti = next_noncomment(tokens, j, n);
        if (fn_ti < n && tokens[fn_ti][0] === "ident") {
          const oldname = tokens[fn_ti][1];
          const outer_scope_end = scopeendfor(ti);
          if (isplaceholder(oldname)) {
            const candidate = pick_candidate("func", oldname, fn_ti, outer_scope_end, false);
            add_rename(oldname, candidate, fn_ti, fn_ti, outer_scope_end);
          } else {
            const chain = scopechainof(fn_ti);
            const innermost = chain.length ? chain[chain.length - 1] : -1;
            add_used(innermost, oldname);
            add_rename(oldname, oldname, fn_ti, fn_ti, outer_scope_end);
          }
        }
        ti = j;
        continue;
      }

      const names = [];
      while (j < n) {
        const t = tokens[j];
        if (t[0] === "ident") {
          const ident_ti = j;
          const ident_name = t[1];
          let type_hint = null;
          j = next_noncomment(tokens, j, n);
          if (j < n && tokens[j][0] === "op" && tokens[j][1] === ":") {
            [type_hint, j] = skip_type_annotation(tokens, j, n);
          }
          names.push([ident_ti, ident_name, type_hint]);
          if (j < n && tokens[j][0] === "op" && tokens[j][1] === ",") {
            j = next_noncomment(tokens, j, n);
            continue;
          } else break;
        } else break;
      }

      if (!names.length) { ti++; continue; }

      const haseq = j < n && tokens[j][0] === "op" && tokens[j][1] === "=";
      let after_rhs_ti = j;
      let rhsparts = [];
      if (haseq) {
        const rhsstart = tokens[j][3];
        const [rhstext, rhsend_pos] = readstmt(code, rhsstart);
        rhsparts = splitcommas(rhstext);
        let first_fn_in_rhs = n;
        let k_scan = j + 1;
        while (k_scan < n && tokens[k_scan][2] < rhsend_pos) {
          if (tokens[k_scan][0] === "kw" && tokens[k_scan][1] === "function") {
            first_fn_in_rhs = k_scan;
            break;
          }
          k_scan++;
        }
        after_rhs_ti = Math.min(k_scan, first_fn_in_rhs);
      }

      const scopeendti = scopeendfor(ti);

      for (let idx = 0; idx < names.length; idx++) {
        const [nameti, oldname, type_hint] = names[idx];
        if (oldname === "_") continue;
        if (oldname.startsWith("_") && !isplaceholder(oldname)) continue;

        let rawname = null;
        let swappedrhs = null;

        if (haseq) {
          const resolver = make_resolver(nameti);
          if (idx < rhsparts.length) {
            swappedrhs = applymap(rhsparts[idx], resolver);
            rawname = infername(swappedrhs);
          } else if (rhsparts.length === 1) {
            swappedrhs = applymap(rhsparts[0], resolver);
            rawname = infer_multireturn(swappedrhs, idx);
          }
        }

        if (!rawname && type_hint) rawname = safeident(type_hint);

        if (!rawname) {
          const alist = assigns.get(oldname) || [];
          for (const [ati, atext] of alist) {
            if (nameti < ati && ati < scopeendti) {
              const swapped = applymap(atext, make_resolver(ati));
              const cand = infername(swapped);
              if (cand) {
                rawname = cand;
                swappedrhs = swapped;
                break;
              }
            }
          }
        }

        if (!rawname && swappedrhs !== null) {
          const stripped_rhs = stripcomments(swappedrhs).trim();
          if (/^\{[\s\S]*\}$/.test(stripped_rhs) && isplaceholder(oldname)) {
            rawname = "Tbl";
          }
        }

        if (!rawname) {
          const chain = scopechainof(nameti);
          const innermost = chain.length ? chain[chain.length - 1] : -1;
          add_used(innermost, oldname);
          add_rename(oldname, oldname, nameti, after_rhs_ti, scopeendti);
          continue;
        }

        const newname = tocamel(rawname);
        const rhs_clean = swappedrhs ? stripcomments(swappedrhs).trim() : "";
        const alist = assigns.get(oldname) || [];
        const is_reassigned_differently = alist.some(
          ([ati, atext]) => nameti < ati && ati < scopeendti && stripcomments(atext).trim() !== newname
        );
        const shadow = Boolean(
          swappedrhs &&
          startswithname(swappedrhs, newname) &&
          (rhs_clean !== newname || is_reassigned_differently)
        );

        const chain = scopechainof(nameti);
        const seenchain = get_seenchain(chain);

        if (newname === oldname && !shadow && !seenchain.has(newname) && !keywords.has(newname)) {
          const innermost = chain.length ? chain[chain.length - 1] : -1;
          add_used(innermost, oldname);
          add_rename(oldname, oldname, nameti, after_rhs_ti, scopeendti);
          continue;
        }

        const candidate = pick_candidate(newname, oldname, nameti, scopeendti, shadow);
        add_rename(oldname, candidate, nameti, after_rhs_ti, scopeendti);
      }

      ti++;
      continue;
    }

    if (tok[0] === "kw" && tok[1] === "function") {
      const func_scope_end = scopeendfor(ti);
      let p_open = next_noncomment(tokens, ti, n);
      while (p_open < n && (tokens[p_open][0] === "ident" || tokens[p_open][0] === "op") && tokens[p_open][1] !== "(") {
        p_open = next_noncomment(tokens, p_open, n);
      }
      if (p_open < n && tokens[p_open][0] === "op" && tokens[p_open][1] === "(") {
        let sig_hints = null;
        const pk1 = prev_noncomment(tokens, ti);
        if (pk1 >= 0 && tokens[pk1][0] === "op" && tokens[pk1][1] === "(") {
          const pk2 = prev_noncomment(tokens, pk1);
          if (pk2 >= 0 && tokens[pk2][0] === "ident" && ["Connect", "Once", "ConnectParallel"].includes(tokens[pk2][1])) {
            const pk3 = prev_noncomment(tokens, pk2);
            if (pk3 >= 0 && tokens[pk3][0] === "op" && (tokens[pk3][1] === "." || tokens[pk3][1] === ":")) {
              const pk4 = prev_noncomment(tokens, pk3);
              if (pk4 >= 0 && tokens[pk4][0] === "ident") {
                const sig_tok_name = tokens[pk4][1];
                const resolved_sig = make_resolver(pk4)(sig_tok_name) || sig_tok_name;
                const base_sig = resolved_sig.replace(/_?\d+$/, "").toLowerCase();
                sig_hints = signalparams[base_sig] || signalparams[sig_tok_name.toLowerCase()] || null;
              }
            }
          }
        }

        const params = [];
        let k = next_noncomment(tokens, p_open, n);
        while (k < n) {
          const pt = tokens[k];
          if (pt[0] === "op" && pt[1] === ")") { k++; break; }
          if (pt[0] === "op" && pt[1] === ".") { k = next_noncomment(tokens, k, n); continue; }
          if (pt[0] === "ident") {
            const p_ti = k;
            const p_name = pt[1];
            let p_type = null;
            k = next_noncomment(tokens, k, n);
            if (k < n && tokens[k][0] === "op" && tokens[k][1] === ":") {
              [p_type, k] = skip_type_annotation(tokens, k, n);
            }
            params.push([p_ti, p_name, p_type]);
            if (k < n && tokens[k][0] === "op" && tokens[k][1] === ",") {
              k = next_noncomment(tokens, k, n);
              continue;
            }
          } else k++;
        }

        const body_start_ti = k;
        for (let p_idx = 0; p_idx < params.length; p_idx++) {
          const [p_ti, p_name, p_type] = params[p_idx];
          if (p_name === "_") continue;
          if (isplaceholder(p_name)) {
            let raw_p = null;
            if (sig_hints && p_idx < sig_hints.length) raw_p = sig_hints[p_idx];
            if (!raw_p && p_type) raw_p = safeident(p_type);
            if (!raw_p) raw_p = infer_param_from_usage(tokens, code, p_name, body_start_ti, func_scope_end, n);
            const new_p = tocamel(raw_p);
            const cand_p = pick_candidate(new_p, p_name, p_ti, func_scope_end, false);
            add_rename(p_name, cand_p, p_ti, p_ti, func_scope_end);
          } else {
            const chain = scopechainof(p_ti);
            const innermost = chain.length ? chain[chain.length - 1] : -1;
            add_used(innermost, p_name);
            add_rename(p_name, p_name, p_ti, p_ti, func_scope_end);
          }
        }
      }
      ti++;
      continue;
    }

    if (tok[0] === "kw" && tok[1] === "for") {
      const loop_scope_end = scopeendfor(ti);
      const loop_vars = [];
      let k = next_noncomment(tokens, ti, n);
      while (k < n) {
        const lt = tokens[k];
        if (lt[0] === "ident") {
          const l_ti = k;
          const l_name = lt[1];
          let l_type = null;
          k = next_noncomment(tokens, k, n);
          if (k < n && tokens[k][0] === "op" && tokens[k][1] === ":") {
            [l_type, k] = skip_type_annotation(tokens, k, n);
          }
          loop_vars.push([l_ti, l_name, l_type]);
          if (k < n && tokens[k][0] === "op" && tokens[k][1] === ",") {
            k = next_noncomment(tokens, k, n);
            continue;
          }
          break;
        } else break;
      }

      if (loop_vars.length && k < n) {
        const sep_tok = tokens[k];
        let do_ti = k + 1;
        let p_depth = 0;
        while (do_ti < n) {
          const dtok = tokens[do_ti];
          if (dtok[0] === "op") {
            if ("([{".includes(dtok[1])) p_depth++;
            else if (")]}".includes(dtok[1]) && p_depth > 0) p_depth--;
          } else if (dtok[0] === "kw" && dtok[1] === "do" && p_depth === 0) break;
          do_ti++;
        }

        if (sep_tok[0] === "op" && sep_tok[1] === "=") {
          const [l_ti, l_name] = loop_vars[0];
          if (isplaceholder(l_name)) {
            const cand = pick_candidate("index", l_name, l_ti, loop_scope_end, false);
            add_rename(l_name, cand, l_ti, do_ti, loop_scope_end);
          } else {
            const chain = scopechainof(l_ti);
            const innermost = chain.length ? chain[chain.length - 1] : -1;
            add_used(innermost, l_name);
            add_rename(l_name, l_name, l_ti, do_ti, loop_scope_end);
          }
        } else if (sep_tok[0] === "kw" && sep_tok[1] === "in") {
          const iter_start_pos = sep_tok[3];
          const iter_end_pos = do_ti < n ? tokens[do_ti][2] : code.length;
          const iter_raw = code.slice(iter_start_pos, iter_end_pos).trim();
          const iter_swapped = applymap(iter_raw, make_resolver(k));

          const is_ipairs = /^ipairs\s*\(/.test(iter_swapped);
          let coll_expr = iter_swapped;
          const m_iter = /^(?:ipairs|pairs)\s*\(([\s\S]+)\)\s*$/.exec(iter_swapped);
          if (m_iter) coll_expr = m_iter[1].trim();
          else {
            const m_next = /^next\s*,\s*([\s\S]+)$/.exec(iter_swapped);
            if (m_next) coll_expr = m_next[1].trim();
          }

          const coll_inferred = infername(coll_expr);
          let val_raw = coll_inferred ? singularize_indexed(coll_inferred) : "Value";
          if (val_raw === coll_inferred && coll_inferred) {
            const m_tag = /GetTagged\s*\(\s*["']([^"']+)["']/.exec(coll_expr);
            if (m_tag) val_raw = normalizeclassname(m_tag[1]);
            else if (!singular_values.has(val_raw)) val_raw = "Value";
          }

          for (let l_idx = 0; l_idx < loop_vars.length; l_idx++) {
            const [l_ti, l_name, l_type] = loop_vars[l_idx];
            if (l_name === "_") continue;
            if (isplaceholder(l_name)) {
              let raw_l;
              if (l_type && safeident(l_type)) raw_l = safeident(l_type);
              else if (l_idx === 0) raw_l = is_ipairs ? "Index" : "Key";
              else if (l_idx === 1) raw_l = val_raw || "Value";
              else raw_l = "Value" + l_idx;
              const new_l = tocamel(raw_l);
              const cand_l = pick_candidate(new_l, l_name, l_ti, loop_scope_end, false);
              add_rename(l_name, cand_l, l_ti, do_ti, loop_scope_end);
            } else {
              const chain = scopechainof(l_ti);
              const innermost = chain.length ? chain[chain.length - 1] : -1;
              add_used(innermost, l_name);
              add_rename(l_name, l_name, l_ti, do_ti, loop_scope_end);
            }
          }
        }
      }
      ti++;
      continue;
    }

    ti++;
  }

  const covered_names = new Map();
  for (const [oldname, , declti, , scopeendti] of renames) {
    if (!covered_names.has(oldname)) covered_names.set(oldname, []);
    covered_names.get(oldname).push([declti, scopeendti]);
  }

  for (const [oldname, assign_list] of assigns.entries()) {
    if (!isplaceholder(oldname)) continue;
    const cov = covered_names.get(oldname) || [];
    for (const [ati, atext] of assign_list) {
      if (cov.some(([dt, et]) => dt <= ati && ati < et)) continue;
      const swapped = applymap(atext, make_resolver(ati));
      const rawname = infername(swapped);
      if (rawname) {
        const newname = tocamel(rawname);
        const cand = pick_candidate(newname, oldname, ati, n, false);
        add_rename(oldname, cand, ati, ati, n);
        cov.push([0, n]);
        covered_names.set(oldname, cov);
        break;
      }
    }
  }

  if (!renames.length) return code;

  const ops = [];
  for (let i = 0; i < n; i++) {
    const tok = tokens[i];
    if (tok[0] !== "ident") continue;
    if (table_keys.has(i) || is_dot_or_colon_access(tokens, i)) continue;
    const rules = renames_by_old.get(tok[1]);
    if (!rules) continue;
    let bestname = null;
    let bestdecl = -1;
    for (const [, newname, declti, activeti, scopeendti] of rules) {
      if ((i === declti || (activeti <= i && i < scopeendti)) && declti > bestdecl) {
        bestname = newname;
        bestdecl = declti;
      }
    }
    if (bestname !== null && bestname !== tok[1]) {
      ops.push([tok[2], tok[3], bestname]);
    }
  }

  if (!ops.length) return code;

  ops.sort((a, b) => a[0] - b[0]);
  const out = [];
  let last = 0;
  for (const [start, end, newtext] of ops) {
    if (start < last) continue;
    out.push(code.slice(last, start), newtext);
    last = end;
  }
  out.push(code.slice(last));
  return out.join("");
}

function doRename() {
  const code = $("input").value;
  if (!code.trim()) {
    setstatus("Nothing to rename", "err");
    return;
  }
  const t0 = performance.now();
  try {
    const result = renamecode(code);
    const ms = Math.round((performance.now() - t0) * 10) / 10;
    $("output").value = result;
    $("copybtn").disabled = false;
    $("downloadbtn").disabled = false;
    setstatus("Done · " + ms + " ms", "ok");
  } catch (err) {
    setstatus(err.message, "err");
  }
}

$("renamebtn").onclick = doRename;

$("input").addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    doRename();
  }
});

$("copybtn").onclick = async () => {
  const txt = $("output").value;
  if (!txt) return;
  try {
    await navigator.clipboard.writeText(txt);
    setstatus("Copied", "ok");
  } catch {
    $("output").select();
    document.execCommand("copy");
    setstatus("Copied", "ok");
  }
};

$("downloadbtn").onclick = () => {
  const txt = $("output").value;
  if (!txt) return;
  const blob = new Blob([txt], {type: "text/plain"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "renamed.luau";
  a.click();
  URL.revokeObjectURL(url);
  setstatus("Downloaded", "ok");
};
</script>
</body>
</html>
"""



_HTML_BYTES = None


def get_html_bytes():
    global _HTML_BYTES
    if _HTML_BYTES is None:
        tables_js = (
            f"const keywords = new Set({json.dumps(sorted(keywords))});\n"
            f"const libmethods = {json.dumps(libmethods)};\n"
            f"const globalfunctions = {json.dumps(globalfunctions)};\n"
            f"const methodnames = {json.dumps(methodnames)};\n"
            f"const signalparams = {json.dumps(signalparams)};\n"
            f"const singularmap = {json.dumps(singularmap)};\n"
            f"const GENERIC_URL_SEGMENTS = new Set({json.dumps(sorted(GENERIC_URL_SEGMENTS))});"
        )
        _HTML_BYTES = html.replace("/*__TABLES__*/", tables_js, 1).encode("utf-8")
    return _HTML_BYTES


class FastThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError:
            pass
        super().server_bind()


class handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = get_html_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b"Not Found"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if self.path != "/rename":
            body = b"Not Found"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(body)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw)
            code = payload.get("code", "")
            t0 = time.perf_counter()
            result = renamecode(code)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
            body = json.dumps({"result": result, "ms": elapsed_ms}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(body)


def runweb(host, port, openbrowser):
    if port is None or port <= 0:
        port = anyport(host)
        if port is None:
            print("No free port found.", file=sys.stderr)
            return 1
    else:
        if not portfree(host, port):
            print(f"Port {port} is in use, picking a free one...", file=sys.stderr)
            port = anyport(host)
            if port is None:
                print("No free port found.", file=sys.stderr)
                return 1
    server = FastThreadingHTTPServer((host, port), handler)
    actualport = server.server_address[1]
    url = f"http://{host}:{actualport}/"
    print(f"Luau Renamer running at {url}")
    print("Press Ctrl+C to stop.")
    if openbrowser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
    return 0


def runterminal(inpath, outpath):
    if inpath:
        try:
            with open(inpath, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except OSError as e:
            print(f"Error reading {inpath}: {e}", file=sys.stderr)
            return 1
    else:
        if sys.stdin.isatty():
            print("Luau Renamer — paste code, then Ctrl+D to rename (Ctrl+C to cancel):", file=sys.stderr)
        code = sys.stdin.read()

    if not code:
        print("No input provided.", file=sys.stderr)
        return 1

    result = renamecode(code)

    if outpath:
        try:
            with open(outpath, "w", encoding="utf-8") as f:
                f.write(result)
        except OSError as e:
            print(f"Error writing {outpath}: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def main():
    p = argparse.ArgumentParser(
        prog="luaurenamer",
        description="Renames Luau variables to inferred camelCase names.",
    )
    p.add_argument("input", nargs="?", default=None,
                   help="Input file (omit to read from stdin)")
    p.add_argument("output", nargs="?", default=None,
                   help="Output file (omit to write to stdout)")
    p.add_argument("--web", action="store_true",
                   help="Launch the web UI instead of terminal mode")
    p.add_argument("--host", default="127.0.0.1",
                   help="Web host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=0,
                   help="Web port (default: 0 = auto random free port)")
    p.add_argument("--no-browser", action="store_true",
                   help="Do not auto-open the browser in web mode")
    args = p.parse_args()

    if args.web:
        return runweb(args.host, args.port, not args.no_browser)
    return runterminal(args.input, args.output)


if __name__ == "__main__":
    sys.exit(main())
