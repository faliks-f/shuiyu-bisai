# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor, image, time
import pyb
from pyb import UART, Timer

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
clock = time.clock()  # Create a clock object to track the FPS.

pipe_threshold = [(31, 164)]
circle_threshold = [(60, 255)]
# circle_threshold = [(23, 255)]
# circle_threshold = [(44, 65)]

pipe_roi = (0, 80, 320, 150)
turn_right_roi = (0, 0, 320, 80)
circle_roi = (80, 120, 160, 110)

go_straight_command = [0X7A, 0XA1, 0X85]
stop_command = [0X7A, 0XA2, 0X85]
turn_right_command = [0X7A, 0XC2, 0X85]
turn_left_command = [0X7A, 0XC1, 0X85]
go_left_command = [0X7A, 0XB1, 0X85]
go_right_command = [0X7A, 0XB2, 0X85]
find_point_command = [0X7A, 0XD1, 0X85]
check_command = [0X7A, 0XFF, 0X85]
# 记录上一次发送的指令，防止反复发送同一指令
record_command = stop_command

# 目前状态是否在转弯的flag
is_turn = False

# left_angle = 90
# right_angle = 90
# UPDATE_LEFT = 0
# UPDATE_RIGHT = 1
# need_update = UPDATE_LEFT

uart = UART(3, 115200)

# 录像的时间，为50s
record_time = 50000

# test_read为True时，从本地文件读取图像
# test_write为True时，会录像
test_read = True
test_write = False

# 判断录像是否已经关闭
close_flag = False

# 记录当前黑点是否已经播报，防止重复报点，当连续几帧没有黑点时复位
find_circle_flag = False
# 记录连续识别到黑点的帧数，达到一定数量时判定有黑点，中间只要一次没识别到黑点就归0
find_circle_times = 0
# 和find_circle_flag功能相同，只不过防止反复识别的是黑线
find_stop_flag = False
# 防止看到黑线时，把黑线识别为圆的flag
find_stop_flag_to_circle = False
# 判断是否是第一次看到黑线
has_seen = False
# 因为需要连续几帧都是别到黑点才判定真的识别到，深水时比较难识别到，所以用这个flag来标识深浅水，深水时判定识别所需要的帧数会降低
max_flag = False
# 和find_circle_times功能相同，只不过是记录找到黑线的帧数
stop_times = 0
# 定时器的一个flag，因为深水时会出现一下状况，连续几帧看到报点，一帧没看到，所有flag归位，又把同一个点连续几帧看到，再次报点
# 所以加了一个定时器，当报深水时，会修改这个flag，同时启动定时器，定时器定时结束调用回调函数时，会修改它的值，以此来防止重复报点
allow_flag = False
# 和allow_flag一个功能，只不过是对黑线计时，第一次看到黑线后等待一段时间后才会继续识别黑线
stop_flag = False


def send(command):
    global record_command
    # 因为record的初值为stop，所以要特殊处理
    if command[1] == 0XA2 or command[1] == 0XFF:
        uart.write(bytearray(command))
    if command[1] != record_command[1]:
        record_command = command
        uart.write(bytearray(command))


def check():
    print("start check")
    while True:
        res = uart.read(3)
        #print(res)
        if res is not None:
            print(res)
            if res[0] == check_command[0] and res[1] == check_command[1] and res[2] == check_command[2]:
                send(check_command)
                break


def start():
    while True:
        res = uart.read(3)
        if res is not None:
            print(res)
            if res[0] == go_straight_command[0] and res[1] == go_straight_command[1] and \
                    res[2] == go_straight_command[2]:
                break


def print_square(b):
    if b is not None:
        print(b.h() * b.w())


def draw(img, b):
    if b is not None:
        img.draw_rectangle(b.rect(), color=0, thickness=2)


def get_max_blob(blobs):
    max_b = None
    for b in blobs:
        square = b.w() * b.w()
        if max_b is None or max_b.w() * max_b.h() < square:
            max_b = b
    return max_b


# def get_max_circle(circles):
#     max_c = None
#     for c in circles:
#         if max_c is None or c.r() > max_c.r():
#             max_c = c
#     return max_c


# def angle_analysis():
#     global left_angle, right_angle
#     if abs(90 - left_angle + right_angle - 90) < 20:
#         send(go_straight_command)
#         print("straight")
#     else:
#         if right_angle - 90 > 25:
#             # right_angle -= 25
#             send(go_left_command)
#             print("left")
#         elif 90 - left_angle > 25:
#             # left_angle += 25
#             send(go_right_command)
#             print("right")
#         elif (90 - left_angle) < (right_angle - 90):
#             send(go_right_command)
#             print("right")
#         else:
#             send(go_left_command)
#             print("left")


def get_pipe_blob(img):
    img.binary(pipe_threshold, True)
    blobs = img.find_blobs([(128, 255)], roi=pipe_roi, x_stride=10, y_stride=10)
    max_b = get_max_blob(blobs)
    return max_b


def turn_right(img, pipe_blob):
    global is_turn
    img.binary(pipe_threshold, True)
    roi = (0, 120, 320, 110)
    # 先获取白色管道的blob
    blobs = img.find_blobs([(128, 255)], roi=roi, x_stride=10, y_stride=10)
    pipe_blob = get_max_blob(blobs)
    # 为None说明看不到白色管道，保持原来指令不动
    if pipe_blob is None:
        return None
    # print(pipe_blob.w(), pipe_blob.h() * 1.4)
    # 当你看到的代表白色管道的blob的宽小于长时，说明转弯结束
    if pipe_blob.w() < pipe_blob.h() and is_turn:
        is_turn = False
        send(go_straight_command)
        print("finish turn")
        return pipe_blob
    # 满足以下条件即代表要转弯了

    if pipe_blob.w() > pipe_blob.h() * 1.5 and (pipe_blob.w() > 85 and pipe_blob.h() > 70) and not is_turn:
        print(pipe_blob.w(), pipe_blob.h())
        is_turn = True
        send(turn_right_command)
        print("turn")
    return pipe_blob
    # img.binary(pipe_threshold, True)
    # blobs = img.find_blobs([(128, 255)], roi=turn_right_roi, x_stride=10, y_stride=10)
    # max_b = get_max_blob(blobs)
    # if max_b is None or max_b.w() * max_b.h() < 2000:
    # if not is_turn:
    # send(turn_right_command)
    # is_turn = True
    # print("turn")
    # else:
    # if is_turn:
    # is_turn = False
    # send(go_straight_command)
    # print("finish turn")
    # return max_b


# def follow(pipe_blob):
#     global is_turn, left_angle, right_angle, need_update
#     if is_turn:
#         return
#     angle = pipe_blob.rotation() / 3.1416 * 180
#     if angle < 90 and need_update == UPDATE_RIGHT:
#         need_update = UPDATE_LEFT
#         left_angle = 90
#     if angle > 90 and need_update == UPDATE_LEFT:
#         need_update = UPDATE_RIGHT
#         right_angle = 90
#     if need_update == UPDATE_LEFT:
#         left_angle = min(angle, left_angle)
#     else:
#         right_angle = max(angle, right_angle)
#     # print(angle, need_update)
#     # print(left_angle, right_angle)
#     angle_analysis()


def follow2(pipe_blob):
    global is_turn
    # 转弯时就不要巡线了
    if is_turn:
        return
    cx = pipe_blob.cx()
    # 以下if判断有些冗余，主要当初是想当偏移过大时用转弯命令来修正，但是发现效果不好
    if 140 < cx < 180:
        # follow(pipe_blob)
        send(go_straight_command)
        # print("straight")
    elif cx < 80:
        send(go_left_command)
        # print("turn left")
        # is_turn = True
    elif cx < 140:
        send(go_left_command)
        # print("left")
    elif 180 < cx < 240:
        send(go_right_command)
        # print("right")
    else:
        send(go_right_command)
        # is_turn = True
        # print("turn right")


def search_circle(img, pipe_blob):
    global circle_roi, find_stop_flag_to_circle, has_seen, stop_flag
    # 当前点已经报过了，直接结束
    if find_stop_flag_to_circle or not has_seen or stop_flag:
        return None
    #print("start search")
    img.binary(circle_threshold, invert=True)
    # 拼接roi，因为黑点一定在管子上，所以传入pipe_blob的目的就是知道管子在图像的哪里
    # 寻找黑点的roi为原先circle_roi和pipe_blob这两个区域中较小的那一个，这样可以保证图像边缘的噪点不会影响
    x = max(pipe_blob.x(), circle_roi[0])
    y = max(pipe_blob.y() + 10, circle_roi[1])
    if x + pipe_blob.w() < 240:
        w = pipe_blob.w()
    else:
        w = max(1, 240 - x)
    if y + pipe_blob.h() < 230:
        h = pipe_blob.h()
    else:
        h = max(1, 230 - y)
    roi = (x, y, w, h)
    # circles = img.find_circles(roi=roi, x_stride=5, y_stride=5, threshold=10, r_min=4, r_max=20)
    # 老流程了，找最大的blob
    blobs = img.find_blobs([(128, 255)], roi=roi, x_stride=5, y_stride=5)
    max_b = get_max_blob(blobs)
    if max_b is None:
        return None
    w, h = max_b.w(), max_b.h()
    # print(min(w, h) / max(w, h))
    # print(w * h)
    # 判断是否满足圆的条件，因为是圆，所以长宽比应该比较接近1，但是实际测下来，长宽比可能为0.3，同时限制最大面积
    #print(min(w, h) / max(w, h), w * h)
    if min(w, h) / max(w, h) > 0.3 and w * h < 5000:
        # print(min(w, h) / max(w, h))
        # print(w * h)
        return max_b
    # max_c = get_max_circle(circles)
    return None


def analysis(c):
    global find_circle_flag, find_circle_times, i, max_flag
    # 比赛时第四第五个为深水，所以适用allow_flag的要求
    # 没有报过这个点
    if find_circle_flag == False:
        # find_circle_times = max(1, find_circle_times + 1)
        # 找到点的帧数加一
        find_circle_times += 1
        # 当找到点的帧数达到max_times时，汇报这个点
        if find_circle_times == 3:
            find_circle_flag = True
            find_circle_times = 0
            i += 1
            print("find", i - 1)
            find_point_command[1] = i - 1
            send(find_point_command)


def handle_timer(timer):
    global allow_flag
    allow_flag = True
    timer.deinit()


def handle_timer2(timer):
    global stop_flag
    stop_flag = False
    timer.deinit()



def stop(img):
    global is_turn, i, stop_flag
    # 转弯的时候就不要找黑线了
    if is_turn and stop_flag:
        return False, None
    img.binary(circle_threshold, invert=True)
    blobs = img.find_blobs([(128, 255)], roi=pipe_roi, x_stride=10, y_stride=10)
    b = get_max_blob(blobs)
    if b is None:
        return False, None
    # print("has")
    w, h = b.w(), b.h()
    # 判断是否满足黑线的条件
    if (0.2 < min(w, h) / max(w, h) and h * w > 4500 and h * w < 8000) and (i == 0 or i >= 9):
        #print(w * h)
        #print(min(w, h) / max(w, h))
        # print(w)
        return True, b
    return False, b


# 先亮红灯，表示没有通过自检
red_led = pyb.LED(1)
red_led.on()

# 如果是读取本地文件，就不要自检
if not test_read:
    check()
    print("check")
    start()
    print("start")
send(go_straight_command)
record_command = check_command

# 亮绿灯，表示开始工作
red_led.off()
green_led = pyb.LED(2)
green_led.on()

# 读取和写入的文件名
if test_read:
    img_reader = image.ImageReader("/stream3.bin")
if test_write:
    img_writer = image.ImageWriter("/stream8.bin")

start = pyb.millis()
i = 0

while (True):
    # try:
    clock.tick()
    if test_read:
        img = img_reader.next_frame(copy_to_fb=True, loop=True)
    else:
        img = sensor.snapshot()
    # 录像
    if test_write:
        img_writer.add_frame(img)
        if pyb.elapsed_millis(start) >= record_time:
            img_writer.close()
            close_flag = True
            test_write = False
    # Do machine vision algorithms on the image here.
    # 找管道的blob
    pipe_blob = get_pipe_blob(img.copy())
    # 返回None或者返回的blob面积太小，都表示没找到管道，直接进入下一帧
    if pipe_blob is None or pipe_blob.w() * pipe_blob.h() < 2000:
        continue
    # img.draw_rectangle(pipe_blob.rect(), color=0, thickness=2)
    # print(max_b.w() * max_b.h())
    # 先看要不要右转
    turn_blob = turn_right(img.copy(), pipe_blob)
    # 再看巡线，注意有全局变量is_turn哦
    follow2(pipe_blob)
    # 找黑线，为了搞定不在第一条黑线就跳出循环，脑细胞都没了，屎山和一堆看名字不知道是干嘛的flag就是从这里来的
    flag, b = stop(img.copy())
    if flag:
        # 没汇报过这条黑黑线
        if not find_stop_flag and not is_turn:
            stop_times += 1
            # 这个flag告诉找黑点的函数不要把黑线当成黑点
            find_stop_flag_to_circle = True
            # has_seen为True，表示第二次看到黑线，即为停止线，因为实际跑的时候停止线只能看到1-2帧，所以只需要一帧就可以判定停止
            # 而第一次看到时，因为刚出发，鱼比较正，能多看到几帧
            if has_seen:
                times = 1
            else:
                times = 4
            if stop_times >= times:
                # 第一次看到，可别停哦
                if not stop_flag:
                    stop_flag = True
                    # 开一个定时器，1.25s之内看到黑线也不许汇报
                    tim = Timer(2, freq=0.8)
                    tim.callback(handle_timer2)
                    stop_flag = True
                    find_circle_flag = True
                    print("stop")
                    find_stop_flag = True
                    # stop_times = 0
                    # breakflag = False
                    # stop_times = 0
                    if has_seen:
                        # send(find_point_command)
                        send(stop_command)
                        # print("stop")
                        i = 0
                        break
                    else:
                        i += 1
                        has_seen = True
    else:
        # 复位一堆flag，这些flag才过去8天再看我就裂开了
        stop_times = max(0, stop_times - 1)
        # stop_times = 0
        if stop_times == 0:
            find_stop_flag_to_circle = False
            find_stop_flag = False
            stop_times = 0
    # 找圆
    c = search_circle(img.copy(), pipe_blob)
    # if is_turn:
    # min_times = -2
    # else:
    # min_times = 0
    # 找到圆
    if c is not None:
        analysis(c)
    # 没找到
    else:
        # find_circle_times = max(min_times, find_circle_times - 1)
        # find_circle_times = max(0, find_circle_times - 1)
        # 实际测试后的结果，这样就是好，别问
        # 有的时候会出现看到3帧，没看到一帧，又看到3帧，然后就过去了，不满足汇报的条件，所以这几个点就成这样了
        find_circle_times = 0
        find_stop_flag_to_circle = False
        find_circle_flag = False
    # 底下有一堆draw，是调试用的
    #draw(img, c)
# if c is not None:
# img.draw_circle(c.x(), c.y(), c.r(), 0, 3)
# draw(img, pipe_blob)
# draw(img, b)
# draw(img, turn_blob)
# print(clock.fps())
# except Exception as e:
# print(e)

# 如果是正常看到黑线停止，那么就关闭，如果是记录了50s停止，那么已经关闭过一次了，不要在关闭
if test_write and not close_flag:
    img_writer.close()

# 蓝灯，表示结束
green_led.off()
blue_led = pyb.LED(3)
blue_led.on()

print("stop")
# 发送停止指令
while True:
    send(stop_command)
