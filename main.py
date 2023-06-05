import os
import sys
import struct
import platform
import subprocess
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker 
from multiprocessing import Pool

#读取震源机制解二进制能量数据文件 hjq
def readBeachBallData(path):
    x = []
    y = []
    f = open(path, 'rb')
    for i in range(3601):
        for j in range(1801):
            data = f.read(4)
            amp = struct.unpack("f", data)[0]
            if amp > 0:
                x.append(i/10)
                y.append(j/10)
    f.close()
    return x, y


def genBeachBallTexture(abspath, paraType, faultType, paras, fileName):
    """
    生成震源机制解沙滩球纹理图片
    paraType: 计算震源机制解的参数类型，MomentTensor-矩张量；FaultPara-断层参数
    faultType： 断层类型， 0-正；1-逆；2-走滑；4-其他
    paras: 震源机制解参数，如果是MomentTensor类型，需要6个参数，mrr mtt mff mrt mrf mtf;如果是FaultPara，需要3个参数，strike dip rake
    fileName: 震源机制解输入文件路径（不带后缀）
    out: 在fileName同目录下输出fileName.dat（能量数据）和fileName.png（沙滩球绘制数据）两个文件
    """
    res = {
        'status':'fail',
        'info':[],
        'data':None,
    }
    dataFile = fileName + ".dat"
    if paraType == "MomentTensor" and len(paras) == 6:
        # 执行命令行程序
        parPath = str(paras[0]) + " " + str(paras[1]) + " " + str(paras[2]) + " " + str(paras[3]) + " " + str(paras[4]) + " " + str(paras[5]) + " " + dataFile
        cur_sys = platform.system()
        if cur_sys == "Windows":
            exePath = os.path.join(abspath, 'calBeachBallData.exe')
            process = subprocess.Popen(exePath + " " + parPath)
            process.wait()
        elif cur_sys == "Linux" or cur_sys == "Darwin":
            exePath = os.path.join(abspath, 'calBeachBallData')
            process = subprocess.Popen(exePath + " " + parPath, shell=True)
            process.wait()
        else:
            res['info'].append("未识别的操作系统:" + cur_sys)
            return res
    elif paraType == "FaultPara" and len(paras) == 3:
        # 执行命令行程序
        parPath = str(paras[0]) + " " + str(paras[1]) + " " + str(paras[2]) + " " + dataFile
        cur_sys = platform.system()
        if cur_sys == "Windows":
            exePath = os.path.join(abspath, 'calBeachBallData.exe')  
            process = subprocess.Popen(exePath + " " + parPath)
            process.wait()
        elif cur_sys == "Linux" or cur_sys == "Darwin":
            exePath = os.path.join(abspath, 'calBeachBallData')          
            process = subprocess.Popen(exePath + " " + parPath, shell=True)
            process.wait()
        else:
            res['info'].append("未识别的操作系统:" + cur_sys)
            return res
    else:
        res['info'].append("类型错误或者类型与参数个数不匹配")
        return res

    x, y = readBeachBallData(dataFile)
  
    plt.rcParams.update({'figure.figsize':(5,4), 'figure.dpi':200})

    # 刻度朝内
    # plt.rcParams['xtick.direction']='in'
    # plt.rcParams['ytick.direction']='in'

    # 0-正断层；1-逆断层；2-走滑断层；3-其他
    if faultType == 0:
        plt.plot(x, y, 'o', color='green', markersize=0.1,  zorder=0)
    elif faultType == 1:
        plt.plot(x, y, 'o', color='red', markersize=0.1,  zorder=0)
    elif faultType == 2:
        plt.plot(x, y, 'o', color='blue', markersize=0.1,  zorder=0)
    else:
        plt.plot(x, y, 'o', color='yellow', markersize=0.1,  zorder=0)

    plt.xlim(0, 360)  # 设置x轴的数值显示范围
    plt.ylim(0, 180)  # 设置y轴的数值显示范围

    # 不显示边框和刻度
    plt.axis('off')
    plt.subplots_adjust(left=0, bottom=0, right=1.0, top=1.0, hspace=0.1, wspace=0.1)

    # 显示边框和刻度
    # plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, hspace=0.1, wspace=0.1)

    # plt.rcParams['font.sans-serif'] = ['SimHei'] #显示中文标签
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.xlabel("方位角", fontsize=14)
    # plt.ylabel("离源角", fontsize=14)
    # x_major_locator=plt.MultipleLocator(60)
    # y_major_locator=plt.MultipleLocator(45)
    # ax=plt.gca()
    # ax.xaxis.set_major_locator(x_major_locator)
    # ax.yaxis.set_major_locator(y_major_locator)
    # ax.axes.xaxis.set_ticklabels([])
    # ax.axes.yaxis.set_ticklabels([])
    # ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%d°'))
    # ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%d°'))

    plt.savefig(fname=fileName+".png")
    plt.close()

    os.remove(dataFile)
    
    res['status'] = "success"
    return res

if __name__ == '__main__':

    WORK_DIR = ''
    if hasattr(sys,'frozen'):
        WORK_DIR = os.path.dirname(sys.executable)
    else:
        WORK_DIR = os.path.dirname(__file__)

    # 多线程运行，提升效率
    pool_size = 10
    pool = Pool(pool_size)

    paraType = sys.argv[1]
    paraNum = int(sys.argv[2])
    if paraType == "MomentTensor":
        for i in range(paraNum):
            faultType = int(sys.argv[8*i+3])
            paras = []
            for j in range(6):
                paras.append(float(sys.argv[8*i+4+j]))
            outfile = sys.argv[8*i+10]
            pool.apply_async(genBeachBallTexture, args=(WORK_DIR, paraType, faultType, paras, outfile))
    elif paraType == "FaultPara":
        for i in range(paraNum):
            faultType = int(sys.argv[5*i+3])
            paras = []
            for j in range(3):
                paras.append(float(sys.argv[5*i+4+j]))
            outfile = sys.argv[5*i+7]
            pool.apply_async(genBeachBallTexture, args=(WORK_DIR, paraType, faultType, paras, outfile))
    
    pool.close()
    pool.join()