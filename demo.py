import os
import sys
import subprocess
import time as t

time1 = t.time()

WORK_DIR = ''
if hasattr(sys,'frozen'):
    WORK_DIR = os.path.dirname(sys.executable)
else:
    WORK_DIR = os.path.dirname(__file__)

# 断层类型集
faultTypeSet = [0,1,2]
paraNum = len(faultTypeSet)

# 参数类型及参数集
paraType = "FaultPara" # 断层参数
parasSet = [[63,44,-104], [107,69,26], [283,89,-177]]

# paraType = "MomentTensor" # 矩张量参数
# parasSet = [
#     [-2.18,1.91,0.27,-0.19,-0.41,0.51],
#     [1.79,-0.67,-2.46,1.22,-0.37,3.47],
#     [-2.28,-1.75,4.03,0.23,-0.11,-5.86]
# ]

# 输出的文件路径集
outfileSet = []
for idx in range(paraNum):
    outfileSet.append("{0}/{1}_{2}".format(WORK_DIR, paraType, idx+1))

# 组织main文件执行输入的参数：沙滩球参数类型|沙滩球数量|第1个沙滩球的断层类型|第1个沙滩球的参数|第1个沙滩球的输出文件路径|...
parPath = ""
parPath += " " + paraType
parPath += " " + str(paraNum)
if paraType == "MomentTensor":
    for i in range(paraNum):
        parPath += " " + str(faultTypeSet[i])
        for j in range(6):
            parPath += " " + str(parasSet[i][j])
        parPath += " " + outfileSet[i]
elif paraType == "FaultPara":
    for i in range(paraNum):
        parPath += " " + str(faultTypeSet[i])
        for j in range(3):
            parPath += " " + str(parasSet[i][j])
        parPath += " " + outfileSet[i]

exePath = os.path.join(WORK_DIR, 'main.py')
process = subprocess.Popen("python "+ exePath + " " + parPath, shell=True)
process.wait()

# 统计耗费时长(s)
time2 = t.time()
print(time2-time1)