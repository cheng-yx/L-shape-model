import pandas as pd 
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os,sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import subprocess

"""解析の溶接変形を実験の溶接変形の差分を初期形状としてモデルに導入したインプットファイルを生成する．

必要なファイル：
・実験結果csvファイル
このフォルダ内にあるもの
・インプットファイル
初期変形を導入したいモデルの.inpファイル
・解析結果csvファイル
溶接終了時のフィールド出力レポート
"""

def SelectFile():
# ファイルダイアログの表示
    # ファイル指定の関数
    def expdialog_clicked():
        fTyp = [("", "*.csv")]
        iFile = os.path.dirname(__file__)
        iFilePath1 = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
        entry1.set(iFilePath1)
    def inpdialog_clicked():
        fTyp = [("", "*.inp")]
        iFile = os.path.dirname(__file__)
        iFilePath2 = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
        entry2.set(iFilePath2)
    def anldialog_clicked():
        fTyp = [("", "welding*.csv")]
        iFile = os.path.dirname(__file__)
        iFilePath3 = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
        entry3.set(iFilePath3)

    # 実行ボタン押下時の実行関数
    def conductMain():
        global filepath
        expPath = entry1.get()
        inpPath = entry2.get()
        anlPath = entry3.get()
        if expPath != "" and inpPath != "" and anlPath != "":
            filepath = (expPath,inpPath,anlPath)
            root.quit()
        else:
            messagebox.showerror("error", "パスの指定がありません")
            sys.exit()

    root = Tk()
    root.title("ファイル参照")

    # Frame1
    frame1 = ttk.Frame(root, padding=10)
    frame1.grid(row=0, column=1, sticky=E)
    expLabel = ttk.Label(frame1, text="実験ファイル＞＞", padding=(5, 2))
    expLabel.pack(side=LEFT)
    entry1 = StringVar()
    expEntry = ttk.Entry(frame1, textvariable=entry1, width=30)
    expEntry.pack(side=LEFT)
    expButton = ttk.Button(frame1, text="参照", command=expdialog_clicked)
    expButton.pack(side=LEFT)

    # Frame2
    frame2 = ttk.Frame(root, padding=10)
    frame2.grid(row=2, column=1, sticky=E)
    inpLabel = ttk.Label(frame2, text="インプットファイル＞＞", padding=(5, 2))
    inpLabel.pack(side=LEFT)
    entry2 = StringVar()
    inpEntry = ttk.Entry(frame2, textvariable=entry2, width=30)
    inpEntry.pack(side=LEFT)
    inpButton = ttk.Button(frame2, text="参照", command=inpdialog_clicked)
    inpButton.pack(side=LEFT)

    # Frame3
    frame3 = ttk.Frame(root, padding=10)
    frame3.grid(row=4, column=1, sticky=E)
    anlLabel = ttk.Label(frame3, text="解析ファイル＞＞", padding=(5, 2))
    anlLabel.pack(side=LEFT)
    entry3 = StringVar()
    anlEntry = ttk.Entry(frame3, textvariable=entry3, width=30)
    anlEntry.pack(side=LEFT)
    anlButton = ttk.Button(frame3, text="参照", command=anldialog_clicked)
    anlButton.pack(side=LEFT)

    # Frame4
    frame4 = ttk.Frame(root, padding=10)
    frame4.grid(row=7,column=1,sticky=W)
    # 実行ボタンの設置
    button1 = ttk.Button(frame4, text="実行", command=conductMain)
    button1.pack(fill = "x", padx=30, side = "left")
    # キャンセルボタンの設置
    button2 = ttk.Button(frame4, text=("閉じる"), command=sys.exit)
    button2.pack(fill = "x", padx=30, side = "left")

    root.mainloop()

def correct_deformation(a_df):
# 板端部の解析変形量を補正
    a_df = a_df.sort_values('Y')
    a_df = a_df.reset_index(drop=True)
    y = a_df.at[0, 'Y']
    a_df.loc[:,'Y'] = a_df.loc[:,'Y'] - y 
    #print(a_df.dtypes)
    a_df.loc[:, 'analysis'] = pd.to_numeric(a_df['analysis']) - pd.to_numeric(a_df.at[0, 'analysis'])
    #a_df.loc[:,'analysis'] = a_df.loc[:,'analysis']-a_df.at[0, 'analysis'] 
    a_df.loc[:,'analysis'] = a_df.loc[:,'analysis']-a_df.loc[:,'Y'] / a_df.at[len(a_df)-1, 'Y'] * a_df.at[len(a_df)-1, 'analysis']
    a_df.loc[:,'Y'] = a_df.loc[:,'Y'] + y
    a_df = a_df.sort_values('label')
    return a_df

def calculate_edge_def(e_df,a_df,edgename,pdffile):
# 板端部の初期変形量を計算
    y_coord = e_df.loc[:,'y'].to_numpy()
    edge_def = e_df.loc[:,edgename].to_numpy()
    fitted_curve = interpolate.Akima1DInterpolator(y_coord, edge_def)
    font = {'family': 'serif', 'serif': 'Times New Roman', 'size': 12}
    a_df.loc[:,'experiment'] = a_df.loc[:,'Y'].apply(lambda y :fitted_curve(y-19.0))
    a_df.loc[:,'initial'] = a_df.loc[:,'experiment'] - a_df.loc[:,'analysis']
    fig = plt.figure()
    plt.scatter(edge_def, y_coord, c="black", label="Experiment",marker="o",s=25)
    plt.scatter(a_df.loc[:,'experiment'].to_list(), a_df.loc[:,'Y'].to_list(), c="gray", label="Interpolation",marker=".",s=9)
    plt.scatter(a_df.loc[:,'analysis'].to_list(), a_df.loc[:,'Y'].to_list(), c="red", label="Analysis",marker=".",s=9)
    plt.scatter(a_df.loc[:,'initial'].to_list(), a_df.loc[:,'Y'].to_list(), c="blue", label="Initial shape",marker=".",s=9)
    plt.grid(axis="x")
    plt.xlabel("Deformation (mm)", size = "large")
    plt.ylabel("$y$ (mm)", size = "large")
    plt.xlim(-3.0, 3.0)
    plt.ylim(0, 500)
    plt.legend(title=edgename+f' ({len(a_df)}nodes)')
    plt.rc('font',**font)
    pdffile.savefig(fig)
    return a_df[['Y','initial']]

if __name__ == "__main__":

    # select Excel and input file -----------------------------------------------------

    SelectFile()
    experimentfile,inputfile,analysisfile = filepath
    
    # read original input data -----------------------------------------------------

    with open(inputfile,'r') as ifile:
        l = ifile.readlines()
        for index,line in enumerate(l):
            if '*Element' in line:
                coord_index = index
                break
        otherdata1 =  l[:9]
        data = l[9:coord_index]  
        otherdata2 =  l[coord_index:]
    with open('temp1.csv','w') as cfile:
        for d in data:
            cfile.write(d)


    # read experiment deformation data -----------------------------------------------------

    e_df = pd.read_csv(experimentfile)

    # read analysis deformation data -----------------------------------------------------

    # 縦板全体の節点データフレーム
    a_df = pd.read_csv(analysisfile, skiprows=1, encoding='shift-jis')
    a_df.columns = ['-','-','-','-','label','X','Y','Z','-','-','-','U1','U2','U3']
    a_df['Y'] = pd.to_numeric(a_df['Y'], errors='coerce')
    a_df = a_df.query('5.0 <= Y <= 495.0') #beadを除いてから2番目node
    a_df = a_df.loc[:,['label','X','Y','Z','U1','U3']]

    # Plate1 --------------------
    a_df['X'] = pd.to_numeric(a_df['X'], errors='coerce')
    a_df['Z'] = pd.to_numeric(a_df['Z'], errors='coerce')
    dfPlate1 = a_df.query('0.0 <= X <= 12.0 and 15.0 <= Z <= 100.0')     # ウェブ1の節点データフレーム
    dfPlate1_edge = dfPlate1.query('X == 6.0 and Z == 100.0')     # ウェブ1の節点データフレーム真中layer
    dfPlate1_edge = dfPlate1_edge.rename(columns={'U1': 'analysis'})   # 変形量をanalysisに
    # Plate2 --------------------
    dfPlate2 = a_df.query('13.0 <= X <= 100.0 and 0.0 <= Z <= 12.0')
    dfPlate2_edge = dfPlate2.query('X == 100.0 and Z == 6.0')
    dfPlate2_edge = dfPlate2_edge.rename(columns={'U3': 'analysis'})


    # correct analysis edge deformation ----------------------------------------------
    dfPlate1_edge = correct_deformation(dfPlate1_edge)
    dfPlate2_edge = correct_deformation(dfPlate2_edge)


    # calculate initial deformation ----------------------------------------------

    # y座標と導入する初期変形を格納したDF（端部のみ）
    pdfname = 'C:\\Users\\cheng\\Desktop\\Docteral Doc\\paper2\\L-Model-Solid\\初期変形\\Initial defomation(edge).pdf'
    pp = PdfPages(pdfname)
    Plate1_initial = calculate_edge_def(e_df=e_df, a_df=dfPlate1_edge, edgename='Plate1',pdffile=pp)
    Plate2_initial = calculate_edge_def(e_df=e_df, a_df=dfPlate2_edge, edgename='Plate2',pdffile=pp)
    pp.close()
    # 初期変形を導入したDFの作成（各縦板）step3
    dfPlate1 = pd.merge(dfPlate1,Plate1_initial, on = 'Y' ,how='left')
    dfPlate1.loc[:,'Z'] = dfPlate1.loc[:,'Z'] + dfPlate1.loc[:,'initial'] * abs(dfPlate1.loc[:,'X']) / 100
    dfPlate1 = dfPlate1.loc[:,['label','X','Y','Z']]

    dfPlate2 = pd.merge(dfPlate2,Plate2_initial, on = 'Y',how='left')
    dfPlate2.loc[:,'Z'] = dfPlate2.loc[:,'Z'] + dfPlate2.loc[:,'initial'] * abs(dfPlate2.loc[:,'X']) / 88
    dfPlate2 = dfPlate2.loc[:,['label','X','Y','Z']]


    # モデルの全節点のラベル、座標を格納したDF
    df = pd.read_csv('temp1.csv', header=None)
    df.columns = ['label','X','Y','Z']

    # 初期変形を導入した部分を入れ替える
    Plate1_label = dfPlate1['label'].to_list()
    Plate2_label = dfPlate2['label'].to_list()

    #print(df.columns)
    for j, i in enumerate(Plate1_label):
        df.iat[int(i) - 1, 3] = dfPlate1.iat[j, 3]
    for j, i in enumerate(Plate2_label):
        df.iat[int(i) - 1, 3] = dfPlate2.iat[j, 3]


    # adjust dataframe for input file ----------------------------------------
    df = df.applymap(lambda x: round(x,8))
    df = df.astype(str)
    for i in ('X','Y','Z'):
        df[i] = df[i].apply(lambda x: x.rstrip('0'))
    df['label'] = df['label'].apply(lambda x: x.rjust(7))
    for i in ('X','Y','Z'):
        df[i] = df[i].apply(lambda x: x.rjust(13))

    # write input data ---------------------------------------------------------
    df.to_csv('temp2.csv', index=False, header=False)
    with open('temp2.csv','r') as file:
        data = file.readlines()
    with open(os.path.join(os.path.dirname(__file__),'ID_'+ os.path.basename(inputfile)),'w') as file:
        for d in otherdata1+data+otherdata2:
            file.write(d)
    os.remove('temp1.csv')
    os.remove('temp2.csv')

print ('Completed')
try:
    subprocess.Popen(pdfname, shell=True)
except:
    print('Close pdf')