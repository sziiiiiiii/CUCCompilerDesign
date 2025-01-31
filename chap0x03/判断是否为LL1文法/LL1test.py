from prettytable import PrettyTable

non_term = set() # 非终结符集合
term = set() # 终结符集合
First = {} # First 集
Follow = {} # Follow 集
Gram = [] # 读入的文法
production = {} #预处理过后的产生式 格式为：'S'：{'a', 'EF'}
AnalysisList = {} # 预测分析表
start_sym = '' # 文法开始符号
end_sym = '#' # 结束符号
epsilon = 'ε' # 空符
isLL1 = True

# 计算 First集
def getFirst() -> None:
    global non_term, term, First
    # 初始化非终结符的First集为空
    for it in non_term: First[it] = set()
    # 初始化终结符的First集合为自己
    for it in term: First[it] = set(it)
    flag = True
    while flag: # 当First集没有更新就结束
        flag = False
        for X in non_term:
            for Y in production[X]:
                i = 0
                mark = True
                while mark and i < len(Y):
                    if not First[Y[i]] - set(epsilon) <= First[X]: # 还存在没有添加的
                        # print('First[' , X, '] = ', "   ", First[X], 'First[', Y[i] , '] = ' , First[Y[i]])
                        # First[Yi] 中没有 ε
                        if epsilon not in First[Y[i]] and Y[i] in non_term and i > 0:
                            First[X] |= First[Y[i]]
                            mark = False
                        else:
                            First[X] |= First[Y[i]] - set(epsilon)
                            flag = True
                    # Yi 不能推出 ε 就标记为 False
                    if epsilon not in First[Y[i]]: mark = False
                    i += 1
                if mark: First[X] |= set(epsilon)
    return None

# 计算 Follow集
def getFollow() -> None:
    global non_term, term, First, Follow, start_sym
    for A in non_term: Follow[A] = set() # 初始化
    Follow[start_sym].add(end_sym) # 1. 将 # 号加入到Follow[s] 中
    flag = True
    while flag: # 当Follow集不再更新，算法结束
        flag = False
        for A in non_term:
            for B in production[A]:
                for i in range(len(B)):
                    # bi 是终结符则跳过
                    if B[i] in term: continue
                    mark = True
                    for j in range(i + 1, len(B)):
                        if not First[B[j]] - set(epsilon) <= Follow[B[i]]: # 可以更新
                            Follow[B[i]] |= First[B[j]] - set(epsilon) # 对应书上的步骤 2
                            flag = True # 发生了改变
                        if epsilon not in First[B[j]]: mark = False
                        break
                    if mark: # A->αBβ and β->ε
                        if not Follow[A] <= Follow[B[i]]: # 可以更新
                            Follow[B[i]] |= Follow[A]
                            flag = True
    return None

# 计算 预测分析表|Select集，并判断是否是LL1文法
def getAnalysisList() -> bool:
    # 初始化
    res = True
    for i in non_term:
        AnalysisList[i] = dict()
        for j in term:
            if j != epsilon: AnalysisList[i][j] = None
        AnalysisList[i][end_sym] = None
    for i in production:
        r = production[i]
        for s in r:
            mark = False
            for si in s:
                if epsilon not in First[si]: # 不能推出空
                    for j in First[si]:
                        if AnalysisList[i][j] != None:
                            AnalysisList[i][j] += ', ->' + s
                            res = False
                        else: AnalysisList[i][j] = s
                    mark = False
                    break
                else:
                    mark = True
                    for j in First[si] - set(epsilon):
                        if AnalysisList[i][j] != None:
                            res = False
                            AnalysisList[i][j] += ', ->' + s
                        else: AnalysisList[i][j] = s
            if mark: #First[s] 可以推出空
                for j in Follow[i]:
                    if AnalysisList[i][j] != None:
                        res = False
                        AnalysisList[i][j] += ', ->' + s
                    else: AnalysisList[i][j] = s
                
    return res



# 打印输出
def printf() -> None:
    global non_term, term, First, Follow, AnalysisList, isLL1
    print("输入的文法如下：")
    for it in Gram: print(' ', it)
    print("非终结符：", end='')
    print(non_term)
    print("终结符：", end='')
    print(term)
    first_follow_table = PrettyTable()
    first_follow_table.field_names = ['非终结符名', 'FIRST集', 'FOLLOW集']
    for it in non_term:
        row = []
        row.append(it)
        row.append(First[it])
        row.append(Follow[it])
        first_follow_table.add_row(row)
    print(first_follow_table)
    print("预测分析表如下：")
    col_data = ['']
    for i in term:
        if i == epsilon: continue
        col_data.append(i)
    col_data.append(end_sym)
    analysis_list_table = PrettyTable(col_data)
    for it in non_term:
        row = []
        row.append(it)
        for i in AnalysisList[it]: 
            if AnalysisList[it][i] == None: row.append('')
            else: row.append('->' + AnalysisList[it][i])
        analysis_list_table.add_row(row)
    print(analysis_list_table)
    if isLL1: print('根据预测分析表可知该文法是LL1文法')
    else: print('根据预测分析表可知该文法不是LL1文法')
    return None

# 主要控制函数
def LL1() -> None:
    global non_term, term, First, Follow, start_sym, Gram, isLL1
    
    n=int(input("请输入表达式个数:"))
    for i in range(n):
        str=input()
        Gram.append(str)

    
    start_sym = Gram[0][0] # 获取文法开始符号
    # 预处理出终结符和非终结符以及产生式
    for it in Gram:
        l, r = it.split('->')
        non_term.add(l)
        r = r.split('|')
        for ri in r: term |= set(ri)
        if l not in production: production[l] = set()
        production[l] |= set(r)
    term -= non_term
    getFirst()
    getFollow()
    isLL1 = getAnalysisList()
    printf()
    return None



if __name__ == '__main__':
    LL1()
    