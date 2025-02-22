import sys,gzip

cnvFileName, samFileName, maskFileName = sys.argv[1:]

masked = {}
if maskFileName.lower() != "none":
    with open(maskFileName) as maskFile:
        for line in maskFile:
            c,s,e = line.strip().split()
            if not c in masked:
                masked[c] = {}
            for i in range(int(s),int(e)+1):
                masked[c][i] = 1

winsize = 1000
depthh = {}
winh = {}
unmaskedLenH = {}
with open(cnvFileName) as cnvFile:
    for line in cnvFile:
        origline = line.strip("\n")
        coords,coords1,freq1,coords2,freq2 = origline.split("\t")
        c,s,e = coords.split(",")
        s,e = int(s), int(e)
        unmaskedLenH[(c, s, e)] = 0
        for pos in range(s, e+1):
            if not c in masked or not pos in masked[c]:
                unmaskedLenH[(c, s, e)] += 1
        if not c in depthh:
            depthh[c] = {}
        depthh[c][(s,e)] = [origline,0]
        winstart = s - (s % winsize)
        winend = e - (e % winsize)
        if not c in winh:
            winh[c] = {}
        w = winstart
        while w <= winend:
            if not w in winh[c]:
                winh[c][w] = []
            winh[c][w].append((s, e))
            w += winsize

headers = ["@HD", "@PG", "@RG", "@SQ"]
if samFileName.endswith(".gz"):
    fopen = gzip.open
else:
    fopen = open
with fopen(samFileName) as samFile:
    for line in samFile:
        if not line[:3] in headers:
            line = line.strip().split("\t")
            read,flag,c,pos1,mapqual,mapinfo,c2,pos2,isize,reads,quals = line[:11]
            isize = int(isize)
            intFlag = int(flag)
            flag = bin(intFlag)
            #the read is the first in a properly mapped proper pair
            if flag[-1] == "1" and flag[-2] == "1" and intFlag <= 512 and isize >= 0:
                assert flag[-3] == "0" and flag[-4] == "0"
                pos = int(pos1)
                w = pos - (pos % winsize)
                if (not c in masked or not pos in masked[c]) and c in winh and w in winh[c]:
                    for s,e in winh[c][w]:
                         if pos >= s and pos <= e:
                            depthh[c][(s,e)][1] += 1

chrs = depthh.keys()
chrs.sort()
for c in chrs:
    keys = depthh[c].keys()
    keys.sort()
    for s,e in keys:
        print("%s\t%s\t%s" %(depthh[c][(s,e)][0],depthh[c][(s,e)][1],unmaskedLenH[(c, s, e)]))
