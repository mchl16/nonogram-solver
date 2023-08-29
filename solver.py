from sys import argv,stdout
from copy import deepcopy as cp
from time import time,sleep
import os

debug=len(argv)>1 and argv[1]=="debug"

threshold=200 # heuristic value used to speed up some calculations, can be changed if needed

start_time = time()

class field:
    def __init__(self,val):
        self.val=val

# union of all 
def union(length,t,constr):
    res=[2 for _ in range(length)] # 2 means that a field has no determined value yet
    for i in t:
        curr=0
        countdown=0
        for j in range(length):
            if curr<len(i) and i[curr]==j:
                countdown=constr[curr]
                curr+=1
            if countdown>0:
                val=1
                countdown-=1
            else:
                val=-1
            if res[j]!=val:
                if res[j]==2: res[j]=val
                else: res[j]=0
    return [(0 if i==2 else i) for i in res]

# check if pattern is a candidate
def maybe_satisfies(line,constr,pattern):
    curr=0
    countdown=0
    for i in range(len(line)):
        if curr<len(pattern) and pattern[curr]==i:
            countdown=constr[curr]
            curr+=1

        if countdown:
            if line[i].val==-1: return False
            countdown-=1
        elif line[i].val==1: return False
        
    return True

from collections import deque
q=deque()

def hash(t):
    return tuple((tuple(i) for i in t))

# generator expression for lines satisfying a given constraint
def gen(S,L,constr):
    if len(constr)==0:
        yield []
        return
    elif len(constr)==1:
        for i in range(0,L-constr[0]+1):
            yield [S+i]
        return
    s=sum(constr[1::])+len(constr)-2 # minimum required length for constraints except the first one
    for i in range(constr[0],L-s):
        res=[S+i-constr[0]]
        for j in gen(S+i+1,L-i-1,constr[1::]): yield res+j

class board:
    def __init__(self,x,y,constr):
        self.t=[[field(0) for _ in range(y)] for _ in range(x)]
        self.x=x
        self.y=y
        self.constr=constr
        self.moves=[[j for j in gen(0,y,i)] for i in self.constr[:x:]]+[[j for j in gen(0,x,i)] for i in self.constr[x::]]

    def __deepcopy__(self,memo):
        result=object.__new__(self.__class__)
        result.t=cp(self.t,memo)
        result.x,result.y=self.x,self.y
        result.constr=self.constr
        result.moves=cp(self.moves,memo)
        return result

    def getline(self,x,i):
        if x>=self.x:
            return self.t[i][x-self.x]
        else: return self[x][i]

    def __getitem__(self,x):
        if x>=self.x:
            return [i[x-self.x] for i in self.t]
        else: return self.t[x]

    # reasoning solver (can detect wrong lines)
    def solve1(self): 
        n,m=self.x,self.y
        credit=n+m
        i=0

        while credit>0:
            # print(i,'?')
            self.moves[i]=list(filter(lambda x: maybe_satisfies(self[i],self.constr[i],x),self.moves[i]))
            if len(self.moves[i])==0: 
                return False
            for j,k in zip(self[i],union(self.x if i>=self.x else self.y,self.moves[i],self.constr[i])): 
                if j.val!=k:
                    j.val=k
                    credit=n+m
            
            if i==n+m-1: i=0
            else: i+=1
            credit-=1
        return True

    # backtrack (attempt every possible line, then filter out those that lead to errors)
    def solve3(self):

        def f(board,i,t):
            # print(t)
            board2=cp(board)
            board2.moves[i]=[t]

            curr=0
            countdown=0
            for j in range(self.x if i>=self.x else self.y):
                if curr<len(self.constr[i]) and t[curr]==j:
                    countdown=self.constr[i][curr]
                    curr+=1
                if countdown>0:
                    board2[i][j].val=1
                    countdown-=1
                else:
                    board2[i][j].val=-1

            # for i2 in board2.t:
            #     for j2 in i2: print('#' if j2.val==1 else ('.' if j2.val==-1 else '?'),end=' ')
            #     print()
            # print()

            return board2.solve1()
        
        def f2(i):
            # print("T:",time()-start_time)
            self.solve1()
            L=len(self.moves[i])
            # print(L)

            def tf(t):
                return list(filter(lambda x: f(self,i,x),t))

            conf=4
            mode=conf if L>conf else L

            if mode==1:
                self.moves[i]=tf(self.moves[i])
                # print(len(self.moves[i])); print()
                return

            L//=mode

            res=[]

            pipes=[os.pipe() for _ in range(mode)]
            pids=[0 for _ in range(mode)]
            for j in range(mode):
                P=pipes[j]
                pids[j]=os.fork()
                if pids[j]==0:
                    if j==mode-1:
                        res2=tf(self.moves[i][j*L::])
                    else:
                        res2=tf(self.moves[i][j*L:(j+1)*L:])
                    os.close(P[0])
                    os.write(P[1],str(res2).encode())
                    os.close(P[1])
                    exit(0)

                os.close(P[1])
            
            for j in range(mode): os.waitpid(pids[j],0)
            for j in range(mode): res=res+eval(os.read(pipes[j][0],213769420).decode())
            for j in range(mode): os.close(pipes[j][0])

            self.moves[i]=res

            # print(len(self.moves[i])); print()

        for i in range(max(self.x,self.y)):
            if i<self.x and len(self.moves[i])<threshold: 
                f2(i)
                self.solve1()
            if i<self.y and len(self.moves[i+self.x])<threshold: 
                f2(i+self.x)
                self.solve1()

    def solve(self):
        def cnt2():
            cnt=0
            for i in range(n):
                for j in range(m):
                    if self.t[i][j].val==0:
                        cnt+=1
            return cnt

        cnt=cnt2()
        while cnt>0:
            self.solve1()
            self.solve3()
            cnt=cnt2()

        with (open("zad_output.txt","w") if not debug else stdout) as g:
            for i in self.t:
                for j in i: g.write('#' if j.val==1 else ('.' if j.val==-1 else '?'))
                g.write('\n')
            exit(0)

def kek():
    if debug:
        t=input()
        n,m=[int(i) for i in t.split()]
        return [t]+[input() for i in range(n+m)]

    with (open("zad_input.txt","r")) as f:
        return [i for i in f]
        


inp=[i for i in kek()]
n,m=[int(i) for i in inp[0].split()]
constr=[[int(i) for i in j.split()] for j in inp[1::]]
B=board(n,m,constr)
B.solve()
