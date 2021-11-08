# 睿抗
### 前言
本文档请配合代码注释使用，存在大量屎山和没有用的代码，有些代码加入后并没有产生作用，后续可以删除  
stream.bin是录像，当时实际场地的录像，可以通过这三个录像那么比赛就没问题了

### 变量详解
#### *_threshold
二值化时的阈值

#### *_roi
find_blobs时的roi

#### *_command
串口通讯的协议

#### 其他的
太烦了，我也代码里了，自己看注释


### 函数功能详解
#### send(command)
串口发送指令

#### check()
上下位机自检，上位机接收到命令后，返回下位机确认码

#### start()
上位机判断是否接收到启动指令，接收后向下位机发送前进指令

#### 有几个打印和绘图方便debug的就不讲了

#### get_max_blob(blobs)
返回面积最大的blob，如果blobs为空，就返回None
> blobs: find_blobs返回的结果  
> return: 面积最大的blob对象或None

#### get_pipe_blob(img)
获取代表白色管道的blob，注意直接返回get_max_blob的结果，所以会返回None
> img: 原图的copy()  
> return: 代表管道的blob或者None

#### turn_right(img, pipe_blob)
判断是否需要转弯的函数，转弯的条件如下
* 第一个条件是blob的宽度为长度的1.5倍，注意，长宽比有一个原则，即判断转弯的条件要宽松，结束转弯的条件要严格，所以这里开始转弯里高要乘1.5，判断结束时不乘
* 第二个条件是因为在从深水进入浅水时会上升的那一段会因为太暗看不见，这里是为了防止在深水进入潜水时误报转弯
* 第三个是为了防止反复发送转弯命令
> img: 原图的copy()   
> pipe_blob:没用到  
> return: 返回一个方便调试的blob，具体看代码注释

#### follow2(pipe_blob)
巡线代码，很简单，不用多说
> pipe_blob: 管道的blob

#### search_circle(img, pipe_blob)
寻找黑点的函数，找到了就返回代表这个黑点的blob，找不到就返回None
> img: 原图的copy()  
> pipe_blob: 管道的blob

#### analysis(c)
分析是否需要汇报这个点
> c: circle的blob

#### stop(img)
寻找黑线
> img: 原图的copy()  
> return: 是否找到黑线的bool值和一个方便debug的blob

### 主流程
看代码