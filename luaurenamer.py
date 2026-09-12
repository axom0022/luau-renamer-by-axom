import re
import sys
import json
import socket
import random
import webbrowser
import threading
import argparse
import bisect
from http.server import BaseHTTPRequestHandler, HTTPServer

keywords = {"and","break","do","else","elseif","end","false","for","function","if","in","local","nil","not","or","repeat","return","then","true","until","while","continue","self"}

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
    "Wait":"Elapsed","Connect":"Connection","Once":"Connection","Clone":"Clone","Destroy":"Destroyed","ClearAllChildren":"Cleared","GetChildren":"Children","GetDescendants":"Descendants","GetPlayers":"PlayerList","GetTagged":"Tagged","GetInstanceAddedSignal":"Signal","GetInstanceRemovedSignal":"Signal","GetDataStore":"DataStore","GetOrderedDataStore":"OrderedDataStore","GetGlobalDataStore":"GlobalDataStore","GetCollisionGroupId":"GroupId","GetCollisionGroupName":"GroupName","CreatePath":"Path","Create":"Created","JSONEncode":"Json","JSONDecode":"Decoded","HttpGetAsync":"Response","HttpPostAsync":"Response","GetAsync":"Value","SetAsync":"Value","UpdateAsync":"Value","IncrementAsync":"Value","Kick":"Kicked","GetMouse":"Mouse","GetPropertyChangedSignal":"Signal","GetAttributeChangedSignal":"Signal","GetAttribute":"Value","SetAttribute":"Attribute","GetPivot":"Pivot","PivotTo":"Pivot","GetFullName":"FullName","GetDebugId":"DebugId","FindFirstAncestor":"Ancestor","FindFirstAncestorOfClass":"Ancestor","FindFirstAncestorWhichIsA":"Ancestor","IsA":"IsType","AddTag":"Tag","RemoveTag":"Tag","HasTag":"HasTag","GetTags":"Tags","WaitForChild":"Child","FindFirstChild":"Child","FindFirstChildOfClass":"Child","FindFirstChildWhichIsA":"Child","SetPrimaryPartCFrame":"Pivot","GetPrimaryPartCFrame":"Pivot","MoveTo":"Pivot","LoadCharacter":"Character","LoadCharacterWithHumanoidDescription":"Character","GetRankInGroup":"Rank","GetRoleInGroup":"Role","IsInGroup":"IsInGroup","IsFriendsWith":"IsFriend","GetFriendsAsync":"Friends","GetUserIdFromNameAsync":"UserId","GetNameFromUserIdAsync":"UserName","GetUserThumbnailAsync":"Thumbnail","GetProductInfo":"ProductInfo","UserOwnsGamePassAsync":"OwnsGamePass","PromptGamePassPurchase":"Prompt","PromptProductPurchase":"Prompt","PromptPurchase":"Prompt","GetDeveloperProductsAsync":"Products","GetStorePages":"Pages","GetService":"Service",
}


def normalizeclassname(name):
    parts = re.split(r"[\s_\-]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def isvalididentifier(s):
    return bool(re.fullmatch(r"[A-Za-z_]\w*", s))


def striptrailingindex(e):
    m = re.match(r'^(.*?)\s*\[[^\]]*\]\s*$', e)
    if m:
        prefix = m.group(1)
        if '.' in prefix or ':' in prefix:
            return prefix
    return e


def startswithname(text, name):
    text = re.sub(r"--.*$", "", text)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped)
    m = re.match(r'^\s*([A-Za-z_]\w*)', stripped)
    return bool(m and m.group(1) == name)


def infername(expr):
    e = re.sub(r"--.*$", "", expr).strip()
    if not e:
        return None
    e = striptrailingindex(e)

    m = re.match(r'^game\s*:\s*GetService\s*\(\s*["\']([^"\']+)["\']\s*\)\s*$', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'[.:]\s*GetService\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^Instance\s*\.\s*new\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^Enum\s*\.\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        t, v = m.group(1), m.group(2)
        n = (t + v) if len(v) <= 1 else v
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'[.:]\s*(?:WaitForChild|FindFirstChild|FindFirstChildOfClass|FindFirstChildWhichIsA)\s*\(\s*["\']([^"\']+)["\']', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*\(', e)
    if m:
        dt, method = m.group(1), m.group(2)
        if method == "new" or method.startswith("from") or method.startswith("look") or method == "Angles" or method == "identity":
            n = dt
        else:
            n = normalizeclassname(method)
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Z][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_]\w*)\s*$', e)
    if m:
        n = normalizeclassname(m.group(2))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-z_]\w*)\s*\.\s*([a-z_]\w*)\s*\(', e)
    if m:
        key = f"{m.group(1)}.{m.group(2)}"
        if key in libmethods:
            n = libmethods[key]
            return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-z_]\w*)\s*\.\s*([a-z_]\w*)\s*$', e)
    if m:
        key = f"{m.group(1)}.{m.group(2)}"
        if key in libmethods:
            n = libmethods[key]
            return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([A-Za-z_]\w*)\s*\(', e)
    if m:
        fn = m.group(1)
        n = globalfunctions.get(fn, fn)
        return n if isvalididentifier(n) and n not in keywords else None

    methods = re.findall(r'[.:]\s*([A-Za-z_]\w*)\s*\(', e)
    if methods:
        method = methods[-1]
        n = methodnames.get(method, normalizeclassname(method))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r"\.\s*([A-Z][A-Za-z0-9_]*)\s*$", e)
    if m:
        n = m.group(1)
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.search(r'\[\s*["\']([A-Z][A-Za-z0-9_]*)["\']\s*\]\s*$', e)
    if m:
        n = normalizeclassname(m.group(1))
        return n if isvalididentifier(n) and n not in keywords else None

    m = re.match(r'^([a-zA-Z_]\w*)\s*$', e)
    if m:
        name = m.group(1)
        if name in keywords:
            return None
        n = name[0].upper() + name[1:] if name[0].islower() else name
        return n if isvalididentifier(n) and n not in keywords else None

    return None


def tokenize(code):
    tokens = []
    i = 0
    n = len(code)
    while i < n:
        c = code[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == "-" and i + 1 < n and code[i + 1] == "-":
            start = i
            if i + 3 < n and code[i + 2] == "[" and code[i + 3] == "[":
                end = code.find("]]", i + 4)
                i = n if end == -1 else end + 2
            else:
                end = code.find("\n", i)
                i = n if end == -1 else end
            tokens.append(("comment", code[start:i], start, i))
            continue
        if c == '"' or c == "'":
            start = i
            q = c
            i += 1
            while i < n and code[i] != q:
                if code[i] == "\\" and i + 1 < n:
                    i += 2
                else:
                    i += 1
            if i < n:
                i += 1
            tokens.append(("string", code[start:i], start, i))
            continue
        if c == "[" and i + 1 < n and (code[i + 1] == "[" or code[i + 1] == "="):
            j = i + 1
            eq = 0
            while j < n and code[j] == "=":
                eq += 1
                j += 1
            if j < n and code[j] == "[":
                close = "]" + "=" * eq + "]"
                end = code.find(close, j + 1)
                stop = n if end == -1 else end + len(close)
                tokens.append(("string", code[i:stop], i, stop))
                i = stop
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


def findscopes(tokens):
    scopes = []
    stack = []
    awaitingdo = False
    for ti, tok in enumerate(tokens):
        if tok[0] != "kw":
            continue
        w = tok[1]
        if w in ("for", "while"):
            awaitingdo = True
            stack.append((ti, False, ti))
        elif w == "do":
            if awaitingdo:
                awaitingdo = False
            else:
                stack.append((ti, False, ti))
        elif w in ("function", "repeat"):
            stack.append((ti, False, ti))
        elif w == "if":
            stack.append((ti, True, ti))
        elif w in ("elseif", "else"):
            if stack and stack[-1][1]:
                openti, _, branchstart = stack.pop()
                scopes.append((branchstart, ti))
                stack.append((openti, True, ti))
        elif w in ("end", "until"):
            if stack:
                openti, isif, branchstart = stack.pop()
                scopes.append((branchstart, ti))
    return scopes


def renamecode(code):
    tokens = tokenize(code)
    n = len(tokens)
    if n == 0:
        return code

    scopes = findscopes(tokens)
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

    usednames = set()
    for ti in range(n - 1):
        if tokens[ti][0] == "kw" and tokens[ti][1] == "local":
            if tokens[ti + 1][0] == "ident":
                usednames.add(tokens[ti + 1][1])

    renames = []
    ti = 0
    while ti < n - 1:
        tok = tokens[ti]
        if tok[0] == "kw" and tok[1] == "local":
            nametok = tokens[ti + 1]
            if nametok[0] == "ident" and ti + 2 < n:
                eqtok = tokens[ti + 2]
                if eqtok[0] == "op" and eqtok[1] == "=":
                    oldname = nametok[1]
                    if not oldname.startswith("_"):
                        exprstart = eqtok[3]
                        lineend = code.find("\n", exprstart)
                        if lineend == -1:
                            lineend = len(code)
                        exprtext = code[exprstart:lineend]
                        newname = infername(exprtext)
                        if newname:
                            shadow = startswithname(exprtext, newname)
                            if not (newname == oldname and not shadow):
                                scopeendti = scopeendfor(ti)
                                if shadow:
                                    candidate = newname + "_2"
                                    suffix = 3
                                else:
                                    candidate = newname
                                    suffix = 2
                                while candidate in usednames or candidate == oldname:
                                    candidate = newname + "_" + str(suffix)
                                    suffix += 1
                                if candidate != oldname:
                                    usednames.add(candidate)
                                    renames.append((oldname, candidate, ti, scopeendti))
        ti += 1

    if not renames:
        return code

    byname = {}
    for oldname, newname, declti, scopeendti in renames:
        byname.setdefault(oldname, []).append((newname, declti, scopeendti))

    ops = []
    for ti, tok in enumerate(tokens):
        if tok[0] != "ident":
            continue
        rules = byname.get(tok[1])
        if not rules:
            continue
        bestname = None
        bestdecl = -1
        for newname, declti, scopeendti in rules:
            if declti <= ti < scopeendti and declti > bestdecl:
                bestname = newname
                bestdecl = declti
        if bestname is not None:
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


def portavailable(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False


def findfreeport(host, low=20000, high=65000, tries=200):
    for _ in range(tries):
        port = random.randint(low, high)
        if portavailable(host, port):
            return port
    for port in range(low, high):
        if portavailable(host, port):
            return port
    return None


html = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<title>Luau Renamer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root, [data-theme="dark"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=2400&q=90");
    --wallpaper-tint: rgba(15, 20, 30, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(255, 255, 255, 0.22);
    --border-strong: rgba(255, 255, 255, 0.40);
    --text: #ffffff;
    --text-dim: rgba(255, 255, 255, 0.72);
    --ok: #6ee7b7;
    --err: #fca5a5;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.35);
    --inner: inset 0 1px 0 rgba(255, 255, 255, 0.20);
  }
  [data-theme="light"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=2400&q=90");
    --wallpaper-tint: rgba(255, 255, 255, 0.10);
    --glass: rgba(255, 255, 255, 0.28);
    --glass-strong: rgba(255, 255, 255, 0.38);
    --glass-soft: rgba(255, 255, 255, 0.20);
    --border: rgba(255, 255, 255, 0.70);
    --border-strong: rgba(255, 255, 255, 1);
    --text: #0f1420;
    --text-dim: rgba(15, 20, 32, 0.68);
    --ok: #047857;
    --err: #b91c1c;
    --btn-bg: rgba(255, 255, 255, 0.42);
    --btn-hover: rgba(255, 255, 255, 0.68);
    --shadow: 0 16px 48px rgba(30, 40, 80, 0.25);
    --inner: inset 0 1px 0 rgba(255, 255, 255, 0.9);
  }
  [data-theme="tokyo"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=2400&q=90");
    --wallpaper-tint: rgba(15, 18, 35, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(180, 200, 255, 0.28);
    --border-strong: rgba(180, 200, 255, 0.55);
    --text: #ffffff;
    --text-dim: rgba(200, 215, 255, 0.75);
    --ok: #9ece6a;
    --err: #f7768e;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(180, 200, 255, 0.22);
  }
  [data-theme="rosepine"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=2400&q=90");
    --wallpaper-tint: rgba(25, 20, 35, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(240, 200, 230, 0.28);
    --border-strong: rgba(240, 200, 230, 0.55);
    --text: #ffffff;
    --text-dim: rgba(240, 220, 240, 0.75);
    --ok: #9ccfd8;
    --err: #eb6f92;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(240, 200, 230, 0.22);
  }
  [data-theme="dracula"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1519681393784-d120267933ba?w=2400&q=90");
    --wallpaper-tint: rgba(20, 18, 35, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(220, 200, 255, 0.28);
    --border-strong: rgba(220, 200, 255, 0.55);
    --text: #ffffff;
    --text-dim: rgba(220, 210, 255, 0.75);
    --ok: #50fa7b;
    --err: #ff5555;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(220, 200, 255, 0.22);
  }
  [data-theme="nord"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=2400&q=90");
    --wallpaper-tint: rgba(40, 48, 64, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(180, 200, 230, 0.28);
    --border-strong: rgba(180, 200, 230, 0.55);
    --text: #ffffff;
    --text-dim: rgba(200, 215, 240, 0.75);
    --ok: #a3be8c;
    --err: #bf616a;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.45);
    --inner: inset 0 1px 0 rgba(180, 200, 230, 0.22);
  }
  [data-theme="gruvbox"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=2400&q=90");
    --wallpaper-tint: rgba(40, 32, 24, 0.40);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(255, 220, 180, 0.28);
    --border-strong: rgba(255, 220, 180, 0.55);
    --text: #ffffff;
    --text-dim: rgba(255, 225, 190, 0.78);
    --ok: #b8bb26;
    --err: #fb4934;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(255, 220, 180, 0.22);
  }
  [data-theme="catppuccin"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=2400&q=90");
    --wallpaper-tint: rgba(30, 25, 45, 0.40);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(220, 200, 255, 0.28);
    --border-strong: rgba(220, 200, 255, 0.55);
    --text: #ffffff;
    --text-dim: rgba(220, 210, 245, 0.78);
    --ok: #a6e3a1;
    --err: #f38ba8;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(220, 200, 255, 0.22);
  }
  [data-theme="onedark"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=2400&q=90");
    --wallpaper-tint: rgba(20, 22, 28, 0.40);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(200, 210, 230, 0.28);
    --border-strong: rgba(200, 210, 230, 0.55);
    --text: #ffffff;
    --text-dim: rgba(200, 215, 235, 0.75);
    --ok: #98c379;
    --err: #e06c75;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(200, 210, 230, 0.22);
  }
  [data-theme="monokai"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5?w=2400&q=90");
    --wallpaper-tint: rgba(30, 28, 20, 0.42);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(255, 230, 180, 0.28);
    --border-strong: rgba(255, 230, 180, 0.55);
    --text: #ffffff;
    --text-dim: rgba(255, 235, 200, 0.78);
    --ok: #a6e22e;
    --err: #f92672;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(255, 230, 180, 0.22);
  }
  [data-theme="kanagawa"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1522543558187-768b6df7c25c?w=2400&q=90");
    --wallpaper-tint: rgba(25, 24, 20, 0.42);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(220, 210, 180, 0.28);
    --border-strong: rgba(220, 210, 180, 0.55);
    --text: #ffffff;
    --text-dim: rgba(220, 215, 190, 0.78);
    --ok: #76946a;
    --err: #c34043;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(220, 210, 180, 0.22);
  }
  [data-theme="everforest"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1448375240586-882707db888b?w=2400&q=90");
    --wallpaper-tint: rgba(30, 35, 25, 0.40);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(200, 220, 190, 0.28);
    --border-strong: rgba(200, 220, 190, 0.55);
    --text: #ffffff;
    --text-dim: rgba(210, 225, 200, 0.78);
    --ok: #a7c080;
    --err: #e67e80;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
    --inner: inset 0 1px 0 rgba(200, 220, 190, 0.22);
  }
  [data-theme="iceberg"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1517299321609-52687d1bc55a?w=2400&q=90");
    --wallpaper-tint: rgba(20, 28, 40, 0.35);
    --glass: rgba(255, 255, 255, 0.06);
    --glass-strong: rgba(255, 255, 255, 0.09);
    --glass-soft: rgba(255, 255, 255, 0.04);
    --border: rgba(180, 210, 235, 0.28);
    --border-strong: rgba(180, 210, 235, 0.55);
    --text: #ffffff;
    --text-dim: rgba(200, 220, 240, 0.78);
    --ok: #8fd3d1;
    --err: #e27878;
    --btn-bg: rgba(255, 255, 255, 0.08);
    --btn-hover: rgba(255, 255, 255, 0.18);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.45);
    --inner: inset 0 1px 0 rgba(180, 210, 235, 0.22);
  }
  [data-theme="matrix"] {
    --wallpaper-image: url("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=2400&q=90");
    --wallpaper-tint: rgba(0, 15, 5, 0.45);
    --glass: rgba(255, 255, 255, 0.05);
    --glass-strong: rgba(255, 255, 255, 0.08);
    --glass-soft: rgba(255, 255, 255, 0.03);
    --border: rgba(120, 255, 150, 0.30);
    --border-strong: rgba(120, 255, 150, 0.60);
    --text: #d0ffd8;
    --text-dim: rgba(180, 255, 200, 0.72);
    --ok: #6ee787;
    --err: #ff6b6b;
    --btn-bg: rgba(120, 255, 150, 0.10);
    --btn-hover: rgba(120, 255, 150, 0.22);
    --shadow: 0 16px 48px rgba(0, 0, 0, 0.55);
    --inner: inset 0 1px 0 rgba(120, 255, 150, 0.25);
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0; padding: 24px;
    font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-feature-settings: "liga" 1, "calt" 1;
    color: var(--text);
    min-height: 100vh;
    transition: color 0.3s;
    position: relative;
    overflow-x: hidden;
    font-size: 13px;
    background: #000;
  }
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: var(--wallpaper-image);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    z-index: -2;
    transition: background-image 0.5s;
  }
  body::after {
    content: "";
    position: fixed;
    inset: 0;
    background: var(--wallpaper-tint);
    z-index: -1;
    transition: background 0.5s;
  }
  #fx {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
  }
  .wrap { position: relative; z-index: 1; max-width: 1600px; margin: 0 auto; }
  .top {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px; gap: 16px; flex-wrap: wrap;
    padding: 14px 22px;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 20px;
    backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    -webkit-backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    box-shadow: var(--shadow), var(--inner);
    transition: background 0.3s, border-color 0.3s;
  }
  h1 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
  }
  [data-theme="light"] h1 { text-shadow: 0 1px 4px rgba(255, 255, 255, 0.6); }
  .controls {
    display: flex; gap: 8px; flex-wrap: wrap;
  }
  .theme-pick {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 14px 5px 16px;
    background: var(--glass-soft);
    border: 1px solid var(--border);
    border-radius: 999px;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    transition: background 0.3s, border-color 0.3s;
  }
  .theme-pick label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.14em;
    color: var(--text-dim); font-weight: 600;
  }
  select {
    appearance: none; -webkit-appearance: none;
    background: transparent;
    color: var(--text);
    border: none;
    padding: 3px 20px 3px 4px;
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    letter-spacing: 0.04em;
    cursor: pointer;
    outline: none;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'/></svg>");
    background-repeat: no-repeat;
    background-position: right 2px center;
    background-size: 10px;
  }
  select option { background: #1a1d24; color: #e6e8eb; font-family: inherit; }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    height: calc(100vh - 220px);
    min-height: 400px;
  }
  .pane {
    display: flex; flex-direction: column; min-height: 0;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 16px;
    backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    -webkit-backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    box-shadow: var(--shadow), var(--inner);
    transition: background 0.3s, border-color 0.3s, box-shadow 0.3s;
  }
  .pane-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px; gap: 10px;
  }
  .pane-title {
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.14em;
    color: var(--text); font-weight: 600;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
  }
  [data-theme="light"] .pane-title { text-shadow: 0 1px 4px rgba(255, 255, 255, 0.7); }
  textarea {
    flex: 1;
    width: 100%;
    padding: 16px;
    background: rgba(0, 0, 0, 0.14);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 14px;
    font-family: inherit;
    font-size: 13px;
    line-height: 1.65;
    resize: none;
    outline: none;
    transition: border-color 0.15s, background 0.3s, color 0.3s;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    letter-spacing: 0.01em;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }
  [data-theme="light"] textarea {
    background: rgba(255, 255, 255, 0.22);
    text-shadow: 0 1px 2px rgba(255, 255, 255, 0.4);
  }
  textarea:focus { border-color: var(--border-strong); background: rgba(0, 0, 0, 0.20); }
  [data-theme="light"] textarea:focus { background: rgba(255, 255, 255, 0.32); }
  textarea::placeholder { color: var(--text-dim); opacity: 0.9; }
  .toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
  button {
    background: var(--btn-bg);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    letter-spacing: 0.04em;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.1s, color 0.3s, box-shadow 0.2s;
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
  }
  [data-theme="light"] button { text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6); }
  button:hover {
    background: var(--btn-hover);
    border-color: var(--border-strong);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22), 0 6px 20px rgba(0, 0, 0, 0.18);
  }
  button:active { transform: scale(0.96); }
  button.primary {
    background: var(--btn-bg);
    border-color: var(--border-strong);
    color: var(--text);
    font-weight: 700;
    padding: 6px 22px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.20);
  }
  button.primary:hover { background: var(--btn-hover); }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  button:disabled:hover { box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14); }
  .bottom-bar {
    display: flex; gap: 10px; margin-top: 16px; align-items: center;
    padding: 12px 22px;
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 999px;
    backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    -webkit-backdrop-filter: blur(30px) saturate(160%) brightness(1.05);
    box-shadow: var(--shadow), var(--inner);
    transition: background 0.3s, border-color 0.3s;
  }
  .status {
    color: var(--text-dim);
    font-size: 11px;
    margin-left: auto;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  }
  [data-theme="light"] .status { text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6); }
  .status.ok { color: var(--ok); }
  .status.err { color: var(--err); }
  input[type=file] { display: none; }
  @media (max-width: 720px) {
    body { padding: 14px; }
    .grid { grid-template-columns: 1fr; height: auto; }
    .pane { height: 340px; }
    .top { padding: 12px 16px; }
    h1 { font-size: 13px; }
  }
</style>
</head>
<body>
  <canvas id="fx"></canvas>
  <div class="wrap">
    <div class="top">
      <h1>Luau Renamer</h1>
      <div class="controls">
        <div class="theme-pick">
          <label for="theme">Theme</label>
          <select id="theme">
            <option value="dark">Dark</option>
            <option value="light">Light</option>
            <option value="tokyo">Tokyo</option>
            <option value="rosepine">Rose Pine</option>
            <option value="dracula">Dracula</option>
            <option value="nord">Nord</option>
            <option value="gruvbox">Gruvbox</option>
            <option value="catppuccin">Catppuccin</option>
            <option value="onedark">One Dark</option>
            <option value="monokai">Monokai</option>
            <option value="kanagawa">Kanagawa</option>
            <option value="everforest">Everforest</option>
            <option value="iceberg">Iceberg</option>
            <option value="matrix">Matrix</option>
          </select>
        </div>
        <div class="theme-pick">
          <label for="fxpick">FX</label>
          <select id="fxpick">
            <option value="none">None</option>
            <option value="particles">Particles</option>
            <option value="rain">Rain</option>
            <option value="snow">Snow</option>
            <option value="stars">Stars</option>
            <option value="aurora">Aurora</option>
            <option value="bubbles">Bubbles</option>
            <option value="fireflies">Fireflies</option>
            <option value="matrix">Matrix</option>
            <option value="confetti">Confetti</option>
            <option value="plasma">Plasma</option>
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
        <textarea id="input" placeholder="Paste your code here..." spellcheck="false"></textarea>
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
        <textarea id="output" placeholder="Renamed code will appear here..." readonly spellcheck="false"></textarea>
      </div>
    </div>
    <div class="bottom-bar">
      <button class="primary" id="renamebtn">Rename</button>
      <span class="status" id="status"></span>
    </div>
  </div>
<script>
const $ = (id) => document.getElementById(id);
const canvas = $("fx");
const ctx = canvas.getContext("2d");
let W = 0, H = 0;
let particles = [];
let currentEffect = "none";
let rafId = null;

function resize() {
  const dpr = window.devicePixelRatio || 1;
  W = window.innerWidth;
  H = window.innerHeight;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width = W + "px";
  canvas.style.height = H + "px";
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  if (currentEffect !== "none") {
    particles = [];
    effects[currentEffect].init();
  }
}

const effects = {
  none: { init() {}, step() {}, draw() {} },
  particles: {
    init() {
      const count = 80;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4, r: Math.random() * 2 + 0.5, a: Math.random() * 0.5 + 0.25 });
      }
    },
    step() {
      for (const p of particles) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < -5) p.x = W + 5; else if (p.x > W + 5) p.x = -5;
        if (p.y < -5) p.y = H + 5; else if (p.y > H + 5) p.y = -5;
      }
    },
    draw() {
      for (const p of particles) {
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255," + p.a + ")"; ctx.fill();
      }
    }
  },
  rain: {
    init() {
      const count = 180;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H, len: Math.random() * 22 + 10, speed: Math.random() * 8 + 5, a: Math.random() * 0.35 + 0.15 });
      }
    },
    step() {
      for (const p of particles) {
        p.y += p.speed;
        if (p.y > H + p.len) { p.y = -p.len; p.x = Math.random() * W; }
      }
    },
    draw() {
      ctx.lineWidth = 1;
      for (const p of particles) {
        ctx.strokeStyle = "rgba(200,220,255," + p.a + ")";
        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x, p.y + p.len); ctx.stroke();
      }
    }
  },
  snow: {
    init() {
      const count = 150;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 2.2 + 0.8, speed: Math.random() * 0.8 + 0.3, wobble: Math.random() * Math.PI * 2, wobbleSpeed: Math.random() * 0.02 + 0.01, a: Math.random() * 0.6 + 0.35 });
      }
    },
    step() {
      for (const p of particles) {
        p.wobble += p.wobbleSpeed; p.y += p.speed; p.x += Math.sin(p.wobble) * 0.6;
        if (p.y > H + 5) { p.y = -5; p.x = Math.random() * W; }
      }
    },
    draw() {
      for (const p of particles) {
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255," + p.a + ")"; ctx.fill();
      }
    }
  },
  stars: {
    init() {
      const count = 220;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.6 + 0.4, phase: Math.random() * Math.PI * 2, speed: Math.random() * 0.04 + 0.01 });
      }
    },
    step() { for (const p of particles) p.phase += p.speed; },
    draw() {
      for (const p of particles) {
        const a = (Math.sin(p.phase) + 1) / 2 * 0.85 + 0.15;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255," + a + ")"; ctx.fill();
      }
    }
  },
  aurora: {
    init() {}, step() {},
    draw() {
      const t = performance.now() * 0.0004;
      const colors = [
        ["rgba(120,255,190,0.20)", "rgba(120,255,190,0)"],
        ["rgba(180,120,255,0.16)", "rgba(180,120,255,0)"],
        ["rgba(120,180,255,0.16)", "rgba(120,180,255,0)"]
      ];
      for (let i = 0; i < 3; i++) {
        const grad = ctx.createLinearGradient(0, 0, W, 0);
        grad.addColorStop(0, colors[i][1]); grad.addColorStop(0.5, colors[i][0]); grad.addColorStop(1, colors[i][1]);
        const baseY = H * 0.35 + i * 90;
        ctx.beginPath(); ctx.moveTo(0, H);
        for (let x = 0; x <= W; x += 12) {
          const y = baseY + Math.sin(x * 0.004 + t + i * 1.5) * 70 + Math.sin(x * 0.009 + t * 1.7) * 30;
          ctx.lineTo(x, y);
        }
        ctx.lineTo(W, H); ctx.closePath(); ctx.fillStyle = grad; ctx.fill();
      }
    }
  },
  bubbles: {
    init() {
      const count = 60;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H + H, r: Math.random() * 18 + 5, speed: Math.random() * 0.9 + 0.4, wobble: Math.random() * Math.PI * 2, wobbleSpeed: Math.random() * 0.02 + 0.01, a: Math.random() * 0.3 + 0.25 });
      }
    },
    step() {
      for (const p of particles) {
        p.wobble += p.wobbleSpeed; p.y -= p.speed; p.x += Math.sin(p.wobble) * 0.5;
        if (p.y < -p.r * 2) { p.y = H + p.r * 2; p.x = Math.random() * W; }
      }
    },
    draw() {
      for (const p of particles) {
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(255,255,255," + p.a + ")"; ctx.lineWidth = 1.4; ctx.stroke();
        ctx.beginPath(); ctx.arc(p.x - p.r * 0.3, p.y - p.r * 0.3, p.r * 0.22, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255," + (p.a + 0.2) + ")"; ctx.fill();
      }
    }
  },
  fireflies: {
    init() {
      const count = 45;
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5, phase: Math.random() * Math.PI * 2, speed: Math.random() * 0.06 + 0.02 });
      }
    },
    step() {
      for (const p of particles) {
        p.phase += p.speed; p.x += p.vx; p.y += p.vy;
        if (Math.random() < 0.015) { p.vx = (Math.random() - 0.5) * 0.6; p.vy = (Math.random() - 0.5) * 0.6; }
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
      }
    },
    draw() {
      for (const p of particles) {
        const glow = (Math.sin(p.phase) + 1) / 2;
        const a = glow * 0.75 + 0.25;
        const r = 2.5 + glow * 2.5;
        const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 6);
        grad.addColorStop(0, "rgba(255,245,160," + a + ")");
        grad.addColorStop(0.35, "rgba(255,220,100," + (a * 0.35) + ")");
        grad.addColorStop(1, "rgba(255,220,100,0)");
        ctx.beginPath(); ctx.arc(p.x, p.y, r * 6, 0, Math.PI * 2); ctx.fillStyle = grad; ctx.fill();
        ctx.beginPath(); ctx.arc(p.x, p.y, r * 0.5, 0, Math.PI * 2); ctx.fillStyle = "rgba(255,255,230," + a + ")"; ctx.fill();
      }
    }
  },
  matrix: {
    init() {
      const fontSize = 14;
      const cols = Math.floor(W / fontSize) + 1;
      for (let i = 0; i < cols; i++) particles.push({ x: i * fontSize, y: Math.random() * H, speed: Math.random() * 3 + 2 });
    },
    step() {
      for (const p of particles) {
        p.y += p.speed;
        if (p.y > H + 30) { p.y = -20; p.speed = Math.random() * 3 + 2; }
      }
    },
    draw() {
      const chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789";
      ctx.font = "14px monospace";
      for (const p of particles) {
        ctx.fillStyle = "rgba(200,255,200,0.95)"; ctx.fillText(chars[Math.floor(Math.random() * chars.length)], p.x, p.y);
        ctx.fillStyle = "rgba(120,255,140,0.55)"; ctx.fillText(chars[Math.floor(Math.random() * chars.length)], p.x, p.y - 14);
        ctx.fillStyle = "rgba(80,220,100,0.30)"; ctx.fillText(chars[Math.floor(Math.random() * chars.length)], p.x, p.y - 28);
        ctx.fillStyle = "rgba(50,180,70,0.14)"; ctx.fillText(chars[Math.floor(Math.random() * chars.length)], p.x, p.y - 42);
      }
    }
  },
  confetti: {
    init() {
      const count = 120;
      const colors = ["#f87171","#fbbf24","#34d399","#60a5fa","#a78bfa","#f472b6","#fb923c","#4ade80"];
      for (let i = 0; i < count; i++) {
        particles.push({ x: Math.random() * W, y: Math.random() * -H, w: Math.random() * 6 + 4, h: Math.random() * 4 + 3, vy: Math.random() * 2 + 1.2, vx: (Math.random() - 0.5) * 1.5, rot: Math.random() * Math.PI * 2, rotSpeed: (Math.random() - 0.5) * 0.15, color: colors[Math.floor(Math.random() * colors.length)] });
      }
    },
    step() {
      for (const p of particles) {
        p.y += p.vy; p.x += p.vx; p.rot += p.rotSpeed;
        if (p.y > H + 20) { p.y = -20; p.x = Math.random() * W; }
        if (p.x < -20) p.x = W + 20;
        if (p.x > W + 20) p.x = -20;
      }
    },
    draw() {
      for (const p of particles) {
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot);
        ctx.fillStyle = p.color; ctx.globalAlpha = 0.85;
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
        ctx.restore();
      }
      ctx.globalAlpha = 1;
    }
  },
  plasma: {
    init() {}, step() {},
    draw() {
      const t = performance.now() * 0.0005;
      for (let y = 0; y < H; y += 12) {
        for (let x = 0; x < W; x += 12) {
          const v = Math.sin(x * 0.008 + t) + Math.sin(y * 0.008 + t * 1.3) + Math.sin((x + y) * 0.006 + t * 0.8) + Math.sin(Math.sqrt(x * x + y * y) * 0.01 + t * 1.5);
          const a = (v + 4) / 8 * 0.12;
          const hue = (v * 60 + t * 40) % 360;
          ctx.fillStyle = "hsla(" + hue + ",80%,60%," + a + ")";
          ctx.fillRect(x, y, 12, 12);
        }
      }
    }
  }
};

function loop() {
  ctx.clearRect(0, 0, W, H);
  const fx = effects[currentEffect];
  fx.step();
  fx.draw();
  rafId = requestAnimationFrame(loop);
}

function setEffect(name) {
  if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
  ctx.clearRect(0, 0, W, H);
  currentEffect = name;
  particles = [];
  if (name === "none" || !effects[name]) return;
  effects[name].init();
  loop();
}

function setstatus(msg, cls) { const s = $("status"); s.textContent = msg; s.className = "status" + (cls ? " " + cls : ""); }

resize();
window.addEventListener("resize", resize);

const storedFx = localStorage.getItem("luaurenamer-fx") || "none";
$("fxpick").value = effects[storedFx] ? storedFx : "none";
setEffect($("fxpick").value);
$("fxpick").onchange = (e) => {
  setEffect(e.target.value);
  localStorage.setItem("luaurenamer-fx", e.target.value);
};

const stored = localStorage.getItem("luaurenamer-theme");
if (stored) { document.documentElement.setAttribute("data-theme", stored); $("theme").value = stored; }
$("theme").onchange = (e) => {
  const t = e.target.value;
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem("luaurenamer-theme", t);
};

$("uploadbtn").onclick = () => $("fileinput").click();
$("fileinput").onchange = (e) => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => { $("input").value = r.result; setstatus("Loaded " + f.name + " · " + f.size + " bytes", "ok"); };
  r.readAsText(f); e.target.value = "";
};
$("clearinput").onclick = () => { $("input").value = ""; $("output").value = ""; $("copybtn").disabled = true; $("downloadbtn").disabled = true; setstatus(""); };
$("renamebtn").onclick = async () => {
  const code = $("input").value;
  if (!code.trim()) { setstatus("Nothing to rename", "err"); return; }
  setstatus("Renaming...");
  const t0 = performance.now();
  try {
    const res = await fetch("/rename", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({code}) });
    if (!res.ok) throw new Error("Server error " + res.status);
    const data = await res.json();
    $("output").value = data.result;
    $("copybtn").disabled = false;
    $("downloadbtn").disabled = false;
    const ms = (performance.now() - t0).toFixed(0);
    setstatus("Done · " + ms + " ms", "ok");
  } catch (err) { setstatus(err.message, "err"); }
};
$("copybtn").onclick = async () => {
  const txt = $("output").value; if (!txt) return;
  try { await navigator.clipboard.writeText(txt); setstatus("Copied", "ok"); }
  catch { $("output").select(); document.execCommand("copy"); setstatus("Copied", "ok"); }
};
$("downloadbtn").onclick = () => {
  const txt = $("output").value; if (!txt) return;
  const blob = new Blob([txt], {type: "text/plain"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "renamed.luau"; a.click();
  URL.revokeObjectURL(url);
  setstatus("Downloaded", "ok");
};
</script>
</body>
</html>
"""


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/rename":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw)
            code = payload.get("code", "")
            result = renamecode(code)
            body = json.dumps({"result": result}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def runweb(host, port, openbrowser):
    if port is None or port <= 0:
        port = findfreeport(host)
        if port is None:
            print("No free port found.", file=sys.stderr)
            return 1
    else:
        if not portavailable(host, port):
            print(f"Port {port} is in use, picking a free one...", file=sys.stderr)
            port = findfreeport(host)
            if port is None:
                print("No free port found.", file=sys.stderr)
                return 1
    server = HTTPServer((host, port), handler)
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
        description="Renames Luau variables to inferred PascalCase names.",
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
