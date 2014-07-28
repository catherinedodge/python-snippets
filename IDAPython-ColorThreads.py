# IDAPython-ColorThreads.py
# This script finds all thread start addresses and colors each thread &
# all descendant functions the same color.
# Functions called by multiple threads are colored grey.
# written by Catherine Dodge


import idaapi
import idautils
import idc

#0xBBGGRR
BLACK = 0x0F0000
RED = 0x6666FF
ORANGE = 0x6699FF
YELLOW = 0xC0FFFF
GREEN = 0x33FF66
LTGREEN = 0x99FF99
BLUE = 0xFF9999
PURPLE = 0xCC6699
PINK = 0x9966FF
GREY = 0x999999

colors = [PINK, ORANGE, PURPLE, LTGREEN, RED, BLUE, YELLOW, GREEN]


def colorAll(params, color):
    """
    Recursively colors all functions in params
    & all callees the given color.

    :param params: a list of function addresses
    :param color: a color, specified as 0xBBGGRR
    """

    # check to see if we're done yet
    lparams = len(params)
    if lparams == 0:
        print "finished with queue"
        return 1

    # color first item in queue, after sanity checks
    funcEA = params[0]
    curFunc = GetFunctionName(funcEA)
    if (curFunc == ""):
        print "Current EA not part of a function!"
        return 1
    curColor = GetColor(funcEA, CIC_FUNC)
    if curColor == 0xFFFFFFFF:
        SetColor(funcEA, CIC_FUNC, color)
    else:
        # if already colored by another thread, color Grey
        SetColor(funcEA, CIC_FUNC, GREY)
    # get the tail iterator
    func_iter = func_tail_iterator_t(get_func(funcEA))

    # use iterator's status to loop
    status = func_iter.main()

    # search rest of this function for calls to add to coloring queue
    while status:
        # get the first function chunk
        chunk = func_iter.chunk()

        # walk the instructions in this basic block
        for head in Heads(chunk.startEA, chunk.endEA):
            inst = idautils.DecodeInstruction(head)
            print inst
            inst = get_current_instruction()
            mnem = inst.get_canon_mnem()

            #If the instruction is a call
            if (mnem == "call"):
                refs = CodeRefsFrom(head, 1)
                refLen = len(refs)
                opType = GetOpType(head, 0)
                callee = GetOpnd(head, 0)
                #print 'call at %s: %x'% (callee, head)

                # check that the call is to a function (not an import & not a register)
                if (refLen > 1) & (opType == 7):
                    callee = GetOpnd(head, 0)
                    flags = GetFunctionFlags(refs[1])

                    # check that the function is a user function (not a library)
                    # & add to work queue
                    if (flags & FUNC_LIB) == 0:
                        #print "not a library - adding to queue"
                        params.append(refs[1])

        # iterate to next chunk of the function
        status = func_iter.next()

    # call this function recursively on new queue
    colorAll(params[1:], color)

if __name__=="__main__":
    # Store addresses of calls to CreateThread & the unique thread starting offsets
    threadCalls = []
    threadOffsets = set()

    # Find "CreateThread" label
    ctAddr = LocByName("CreateThread")
    if ctAddr != BADADDR:

        # Find all data xrefs to CreateThread import
        # (there are no code xrefs)
        ctDataXrefs = DataRefsTo(ctAddr)

        # Validate that they're "call" instructions
        for dRef in ctDataXrefs:
            inst = idautils.DecodeInstruction(dRef);
            print inst[0]
            #inst = get_current_instruction()
            mnem = inst[0]

            #If the instruction is a call, find thread start offset
            if (mnem == "call"):
                #print "call to CreateThread: %x" % dRef
                threadCalls.append(dRef)

                # count "push"es going backwards
                # 3rd will be the instruction pushing start offset
                pushCount = 0
                curEA = dRef
                while pushCount < 3:
                    curEA = PrevHead(curEA, MinEA())
                    ua_ana0(curEA);
                    inst = get_current_instruction()
                    mnem = inst.get_canon_mnem()
                    if (mnem == "push"):
                        pushCount += 1
                # get address of offset start
                pushRef = DataRefsFrom(curEA)
                for pRef in pushRef:
                    threadOffsets.add(pRef)

    # extract all the offsets we identified & color
    offsetCount = len(threadOffsets)
    while offsetCount != 0:
        startOffset = threadOffsets.pop()
        colorList = [startOffset]
        #print "thread start set: %x" % startOffset
        #print "calling colorAll with list element %i" % offsetCount
        colorAll(colorList, colors[offsetCount])
        offsetCount -= 1
