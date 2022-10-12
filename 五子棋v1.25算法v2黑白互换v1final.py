# v1.21解决算法
# v1.24加入划三、冲四检测机制 ,美化v1
# v1.25美化v2,黑白互换
# 待解决:

import pygame, sys, time, random

SCREEN_WIDTH, SCREEN_HEIGHT = 770, 655
BOARD_ORDER, BOARD_SIZE = 19, 30  # 棋盘的阶数，每格宽度(像素)
BOARD_X0, BOARD_Y0 = 15, 15  # 棋盘网格的左上角在棋盘画布上的坐标
GRID_NULL, GRID_BLACK, GRID_WHITE = 0, 1, 2  # 落子位置状态
SPEED_X = [1, 0, 1, -1]  # 四个方向矢量定义
SPEED_Y = [0, 1, 1, 1]  # 0：横；1：竖；2：左上到右下；3：右上到左下
ATK = 1  # ATK越大，越aggresive
DEF = 3 / 2  # DEF越大,越stable
WIN_SCORE = 0xfffffff  # 即只要分数达到WIN_SCORE，就会win
PRE_WIN_SCORE = WIN_SCORE // 10  # 即只要分数达到WIN_SCORE，就要win
SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 1000
SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 100, 20, 16, 2
SELF_NAME = "Gobang AI"
OPPO_NAME = str(input("player name is:"))
print('请移步pygame窗口选择操作者执子颜色')
SELF_POS, OPPO_POS = (810, 500), (810, 600)


def is_five(grid, x, y, man):  # 判断是否五子连珠
    for flag in (0, 1, 2, 3):  # 从一子开始沿四个方向矢量判断
        posiNum, negaNum = 0, 0  # 方向矢量正负方向上的连子数
        for i in range(-1, -5, -1):  # 正方向搜索四次
            tx, ty = x + i * SPEED_X[flag], y + i * SPEED_Y[flag]
            if tx < 0 or tx >= BOARD_ORDER or ty < 0 or ty >= BOARD_ORDER:
                break
            if grid[ty][tx] != man:
                break
            negaNum += 1
        for i in range(1, 5, 1):  # 负方向搜索四次
            tx, ty = x + i * SPEED_X[flag], y + i * SPEED_Y[flag]
            if tx < 0 or tx >= BOARD_ORDER or ty < 0 or ty >= BOARD_ORDER:
                break
            if grid[ty][tx] != man:
                break
            posiNum += 1
        if negaNum + posiNum + 1 >= 5:
            return True
    return False


def RT_draw_txt(scr, fnt, cls, txt, x, y):  # 以x,y为左上角输出字幕
    pic = fnt.render(txt, True, cls)
    scr.blit(pic, (x, y))
    return


ASSESS_WIN, ASSESS_ANS, ASSESS_COUNT = 2, 1, 0


def RT_deep_search(grid):  # 返回需要判断的子坐标
    Rad = 1  # 返回棋子周围的Rad圈的子
    pList = []
    for y in range(BOARD_ORDER):
        for x in range(BOARD_ORDER):
            if grid[y][x] == GRID_NULL:  # 空位置
                flag = 0
                for i in range(y - Rad, y + Rad + 1):
                    for j in range(x - Rad, x + Rad + 1):
                        if i >= 0 and i < BOARD_ORDER - 1 and 0 <= j < BOARD_ORDER - 1:
                            if grid[i][j] != 0:  # 周围一圈有落子
                                # print()
                                pList.append([x, y])
                                flag = 1
                                break
                    if flag == 1:
                        break
    '''
    pos_score = [[(7 - max(abs(x - 7), abs(y - 7))) for x in range(BOARD_ORDER)] for y in range(BOARD_ORDER)]
    sortList = [[0,0,0] for l in range(len(pList))]
    for i in range(len(pList)):
        sortList[i][0] = pos_score[pList[i][1]][pList[i][0]]
        sortList[i][1] = pList[i][0]
        sortList[i][2] = pList[i][1]
    sortList.sort(reverse=True)
    for s in range(len(sortList)):
        pList[s][0] = sortList[s][1]
        pList[s][1] = sortList[s][2]
    '''
    return pList


FIVE = 7
FOUR, THREE, TWO = 6, 4, 2
SFOUR, STHREE, STWO = 5, 3, 1


class CLS_gobang(object):
    def __init__(self, fPic, bPic, wPic, x0, y0):
        self.facePic, self.bMan, self.wMan = fPic, bPic, wPic  # self图片

        # 不同的字体
        self.font = pygame.font.Font(None, 32)
        self.fontScore = pygame.font.Font(None, 16)
        self.fontWin = pygame.font.Font(None, 80)
        self.fontStep = pygame.font.Font(None, 20)
        self.fontName = pygame.font.Font(None, 36)

        self.x0, self.y0 = x0, y0  # 棋盘左上角坐标

        self.board = pygame.Surface((570, 570))  # board对象是个surface
        self.draw_board()  # 绘制board
        self.grid_init()  # 生成board信息
        self.sysStat = 0  # 决出胜负?
        self.winner = -1
        self.roundNum = 0
        self.color = GRID_NULL
        self.playerColor = GRID_NULL
        # self.FirstStepList = [[8,8],[8,9],[8,10],[9,8],[9,10],[10,8],[10,9],[10,10]] #当AI执黑时，记录黑棋开局第二子可下位置，用于帮助AI下第二子
        # newestOppoStep = [-1,-1]  #当AI执黑时，记录白棋最新走向，只用于帮助AI开局下第二子
        self.turn = GRID_NULL  # 现在谁刚下好，只判断奇偶性,用于判断谁该下
        self.newestChessPos = [-5, -5]  # 最新的一步棋，用于突出那步棋
        self.black_pos_x, self.black_pos_y = (0, 0)
        self.white_pos_x, self.white_pos_y = (0, 0)
        self.WHITE_PLAYER_NAME, self.BLACK_PLAYER_NAME = 0, 0
        return

    def draw_board(self):  # 绘制棋盘
        self.board.fill((240, 200, 0))  # 填充底色
        L = BOARD_X0 + (BOARD_ORDER - 1) * BOARD_SIZE  # board的内框边长/右下角坐标
        for i in range(BOARD_X0, SCREEN_HEIGHT, BOARD_SIZE):
            pygame.draw.line(self.board, (0, 0, 0), (BOARD_X0, i), (L, i), 1)  # 绘制横线
            pygame.draw.line(self.board, (0, 0, 0), (i, BOARD_Y0), (i, L), 1)  # 绘制竖线
        # 加粗中线
        pygame.draw.line(self.board, (0, 0, 0), (BOARD_X0, BOARD_Y0 + (BOARD_ORDER // 2) * BOARD_SIZE),
                         (L, BOARD_Y0 + (BOARD_ORDER // 2) * BOARD_SIZE), 2)
        pygame.draw.line(self.board, (0, 0, 0), (BOARD_X0 + (BOARD_ORDER // 2) * BOARD_SIZE, BOARD_Y0),
                         (BOARD_X0 + (BOARD_ORDER // 2) * BOARD_SIZE, L), 2)
        pygame.draw.rect(self.board, (0, 0, 0), (BOARD_X0 - 1, BOARD_Y0 - 1, L + 3 - BOARD_X0, L + 3 - BOARD_Y0),
                         1)  # 加粗外框(以画空心矩形方式实现)
        # 画五个小正方形
        rec_size = 8
        pos = [(3, 3), (15, 3), (3, 15), (15, 15), (9, 9)]
        for (x, y) in pos:
            pygame.draw.rect(self.board, (0, 0, 0), (
            BOARD_X0 + x * BOARD_SIZE - rec_size // 2, BOARD_X0 + y * BOARD_SIZE - rec_size // 2, rec_size, rec_size))

        return

    def grid_init(self):  # 虚拟棋盘(数字信息)初始化
        self.grid = []
        self.stepGrid = [[0 for x in range(BOARD_ORDER)] for y in range(BOARD_ORDER)]
        for y in range(BOARD_ORDER):
            line = [GRID_NULL] * BOARD_ORDER  # 生成第二维列表
            self.grid.append(line)  # 添加到一维列表中
        # m = BOARD_ORDER//2
        # self.grid[m][m] = GRID_BLACK #中间落子
        return

    def draw_chess(self, scr):  # 遍历棋盘,绘制黑白子和步数  v1.24 现在谁下
        sx, sy = BOARD_SIZE * 5 // 12, BOARD_SIZE * 5 // 12
        # 绘制双方执子示意子
        scr.blit(self.bMan, (self.black_pos_x, self.black_pos_y))
        scr.blit(self.wMan, (self.white_pos_x, self.white_pos_y))
        # 将要下的人子外画框
        # print('check')
        if self.turn == GRID_BLACK:  # 黑子下完，画白子的框
            pygame.draw.rect(scr, (200, 100, 150), (WHITE_POS_X, WHITE_POS_Y, IMG_LEN, IMG_LEN), 3)
        elif self.turn == GRID_WHITE:
            pygame.draw.rect(scr, (200, 100, 150), (BLACK_POS_X, BLACK_POS_Y, IMG_LEN, IMG_LEN), 3)

        pygame.draw.rect(scr, (250, 0, 100), (
        self.x0 + self.newestChessPos[0] * BOARD_SIZE, self.y0 + self.newestChessPos[1] * BOARD_SIZE, IMG_LEN, IMG_LEN),
                         2)

        for y in range(BOARD_ORDER):
            for x in range(BOARD_ORDER):

                pos = (self.x0 + x * BOARD_SIZE + BOARD_SIZE // 2, self.y0 + y * BOARD_SIZE + BOARD_SIZE // 2)
                if self.grid[y][x] == GRID_BLACK:
                    scr.blit(self.bMan, (self.x0 + x * BOARD_SIZE, self.y0 + y * BOARD_SIZE))
                    msg_image = self.fontStep.render(str(self.stepGrid[y][x] + 2 - self.color), True, (200, 200, 200),
                                                     (0, 0, 0))
                    msg_image_rect = msg_image.get_rect()
                    msg_image_rect.center = pos
                    screen.blit(msg_image, msg_image_rect)

                elif self.grid[y][x] == GRID_WHITE:
                    scr.blit(self.wMan, (self.x0 + x * BOARD_SIZE, self.y0 + y * BOARD_SIZE))
                    msg_image = self.fontStep.render(str(self.stepGrid[y][x] + 2 - self.color), True, (50, 50, 50),
                                                     (255, 255, 255))
                    msg_image_rect = msg_image.get_rect()
                    msg_image_rect.center = pos
                    screen.blit(msg_image, msg_image_rect)

        return

    def draw(self, scr):  # 绘制 棋盘外环境
        pygame.display.update()
        scr.fill((180, 140, 0))
        scr.blit(self.facePic, (0, 0))
        scr.blit(self.board, (self.x0, self.y0))  # 绘制棋盘
        self.draw_chess(scr)
        if self.sysStat == 1:  # 决出胜负
            txt, cls = (self.WHITE_PLAYER_NAME + ' WIN !!'), (0, 50, 255)  # 先默认玩家赢
            if self.winner == GRID_BLACK:  # 若玩家输,再改
                txt, cls = (self.BLACK_PLAYER_NAME + ' WIN !!'), (0, 50, 255)
            msg_image = self.fontWin.render(txt, True, cls)
            screen.blit(msg_image, (BOARD_X0 + 40, BOARD_Y0 + 90))
        txt, cls = SELF_NAME, (255, 255, 255)
        RT_draw_txt(scr, self.fontName, cls, txt, 610, 503)
        txt, cls = OPPO_NAME, (255, 255, 255)
        RT_draw_txt(scr, self.fontName, cls, txt, 610, 611)

        return

    def getPointScore_mine(self, count, ocount, man):  # man->主动考虑方->宁可舍活四、冲四,也不留对方冲四
        Mscore, Oscore = 0, 0
        if True:
            if True:
                if count[FIVE] > 0:
                    return (15 * WIN_SCORE, 0)
                if count[FOUR] > 0:
                    Mscore = WIN_SCORE * 2
                if count[SFOUR] > 1:
                    Mscore += 7 * WIN_SCORE // 4
                elif (count[SFOUR] > 0 and count[THREE] > 0):
                    Mscore += WIN_SCORE * 3 // 2
                elif count[SFOUR] > 0:
                    Mscore += count[THREE]
                if count[THREE] > 1:
                    Mscore += PRE_WIN_SCORE
                elif count[THREE] > 0:
                    Mscore += SCORE_THREE
                if count[STHREE] > 0:
                    Mscore += count[STHREE] * SCORE_STHREE
                if count[TWO] > 0:
                    Mscore += count[TWO] * SCORE_TWO
                if count[STWO] > 0:
                    Mscore += count[STWO] * SCORE_STWO

                if ocount[FOUR] > 0:
                    Oscore = SCORE_FOUR
                if ocount[SFOUR] >= 1:
                    return (0, 3 * WIN_SCORE)
                if ocount[THREE] >= 1:
                    Oscore += WIN_SCORE
                if ocount[STHREE] > 0:
                    # print('Oscore +=',ocount[STHREE], '*', SCORE_STHREE ,'*',DEF)
                    Oscore += ocount[STHREE] * SCORE_STHREE * DEF
                if ocount[TWO] > 0:
                    Oscore += ocount[TWO] * SCORE_TWO * DEF
                if ocount[STWO] > 0:
                    Oscore += ocount[STWO] * SCORE_STWO
                # print("score=",score)
                return (Mscore, Oscore)

    def getPointScore_oppo(self, count, ocount, man):  # man->主动考虑方 目的->防对方下一步的双三/冲四划三
        Mscore, Oscore = 0, 0
        if True:
            if True:
                if count[FIVE] > 0:
                    return (5 * WIN_SCORE, 0)
                if count[SFOUR] > 1:
                    Mscore += count[SFOUR] * SCORE_SFOUR
                elif (count[FOUR] > 0 and count[THREE]) > 0:
                    Mscore += PRE_WIN_SCORE * 7
                elif (count[SFOUR] > 0 and count[THREE]) > 0:
                    Mscore += PRE_WIN_SCORE * 5
                if count[THREE] > 1:
                    Mscore += 4 * PRE_WIN_SCORE
                if count[STHREE] > 0:
                    Mscore += count[STHREE] * SCORE_STHREE
                if count[TWO] > 0:
                    Mscore += count[TWO] * SCORE_TWO
                if count[STWO] > 0:
                    Mscore += count[STWO] * SCORE_STWO

                return (Mscore, Oscore)

    def is_it_real_s4(self, pos, dir_index, man):
        x, y = pos
        mine = GRID_BLACK + GRID_WHITE - man
        opponent = man
        is_it = 1
        temp_count = [0] * 8
        directions = [[1, 0], [0, 1], [1, 1], [-1, 1]]
        for i in range(4):
            if i != dir_index:
                self.analysisLine(self.grid, x, y, i, directions[i], mine, opponent, temp_count, False, False, False)
        if ((temp_count[4] + temp_count[5] + temp_count[6] + temp_count[7]) >= 1):
            is_it = 0
        # if pos == (12,7):
        #     print( 'check if is s4 at pos 12 7 ,test person=',mine,'\tis_it?',is_it)

        return is_it

    def is_it_real_3(self, pos, dir_index, man):
        x, y = pos
        mine = GRID_BLACK + GRID_WHITE - man
        opponent = man
        is_it = 1
        temp_count = [0] * 8
        directions = [[1, 0], [0, 1], [1, 1], [-1, 1]]
        for i in range(4):
            if i != dir_index:
                self.analysisLine(self.grid, x, y, i, directions[i], mine, opponent, temp_count, False, False, False)
        if ((temp_count[4] + temp_count[5] + temp_count[6] + temp_count[7]) >= 1):
            is_it = 0

        return is_it

    def getLine(self, board, x, y, dir_offset, mine, opponent):
        line = [0] * 9

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            if (tmp_x < 0 or tmp_x >= BOARD_ORDER or tmp_y < 0 or tmp_y >= BOARD_ORDER):
                line[i] = opponent  # set out of range as opponent chess
            else:
                line[i] = board[tmp_y][tmp_x]

        return line

    def analysisLine(self, board, x, y, dir_index, dir_offset, mine, opponent, count, RECORD=True, s4=True,
                     check3=True):
        if True:
            if True:
                def setRecord(self, x, y, left, right, dir_index, dir_offset):
                    tmp_x = x + (-5 + left) * dir_offset[0]
                    tmp_y = y + (-5 + left) * dir_offset[1]
                    for i in range(left, right + 1):
                        tmp_x += dir_offset[0]
                        tmp_y += dir_offset[1]
                        self.record[tmp_y][tmp_x][dir_index] = 1

                empty = GRID_NULL
                left_idx, right_idx = 4, 4

                line = self.getLine(board, x, y, dir_offset, mine, opponent)
                # print(line)

                while right_idx < 8:
                    if line[right_idx + 1] != mine:
                        break
                    right_idx += 1
                while left_idx > 0:
                    if line[left_idx - 1] != mine:
                        break
                    left_idx -= 1

                left_range, right_range = left_idx, right_idx
                while right_range < 8:
                    if line[right_range + 1] == opponent:
                        break
                    right_range += 1
                while left_range > 0:
                    if line[left_range - 1] == opponent:
                        break
                    left_range -= 1

                chess_range = right_range - left_range + 1
                if chess_range < 5:
                    if RECORD:
                        setRecord(self, x, y, left_range, right_range, dir_index, dir_offset)
                    return 0

                if RECORD:
                    setRecord(self, x, y, left_idx, right_idx, dir_index, dir_offset)

                m_range = right_idx - left_idx + 1

                # M:mine chess, P:opponent chess or out of range, X: empty
                if m_range >= 5:
                    count[FIVE] += 1

                # Live Four : XMMMMX
                # Chong Four : XMMMMP, PMMMMX
                if m_range == 4:
                    left_empty = right_empty = False
                    if line[left_idx - 1] == empty:
                        left_empty = True
                    if line[right_idx + 1] == empty:
                        right_empty = True
                    if left_empty and right_empty:
                        count[FOUR] += 1
                    elif (left_empty) and (s4 == True):
                        pos = x - (4 - left_idx + 1) * dir_offset[0], y - (4 - left_idx + 1) * dir_offset[1]
                        count[SFOUR] += self.is_it_real_s4(pos, dir_index, mine)
                    elif (right_empty) and (s4 == True):
                        pos = x + (right_idx - 4 + 1) * dir_offset[0], y + (right_idx - 4 + 1) * dir_offset[1]
                        count[SFOUR] += self.is_it_real_s4(pos, dir_index, mine)
                    elif left_empty or right_empty:
                        count[SFOUR] += 1

                # Chong Four : MXMMM, MMMXM, the two types can both exist
                # Live Three : XMMMXX, XXMMMX
                # Sleep Three : PMMMX, XMMMP, PXMMMXP
                if m_range == 3:
                    if True:
                        left_empty = right_empty = False
                        left_four = right_four = False
                        if line[left_idx - 1] == empty:
                            if line[left_idx - 2] == mine:  # MXMMM
                                if RECORD:
                                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir_offset)
                                if (s4 == True):
                                    pos = x - (4 - left_idx + 1) * dir_offset[0], y - (4 - left_idx + 1) * dir_offset[1]
                                    count[SFOUR] += self.is_it_real_s4(pos, dir_index, mine)
                                else:
                                    count[SFOUR] += 1
                                left_four = True
                            left_empty = True

                        if line[right_idx + 1] == empty:
                            if line[right_idx + 2] == mine:  # MMMXM
                                if RECORD:
                                    setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir_offset)
                                if (s4 == True):
                                    pos = x + (right_idx - 4 + 1) * dir_offset[0], y + (right_idx - 4 + 1) * dir_offset[
                                        1]
                                    count[SFOUR] += self.is_it_real_s4(pos, dir_index, mine)
                                else:
                                    count[SFOUR] += 1
                                right_four = True
                            right_empty = True

                        if left_four or right_four:
                            pass
                        elif left_empty and right_empty:
                            if chess_range > 5:  # XMMMXX, XXMMMX
                                if check3:
                                    pos1 = x - (4 - left_idx + 1) * dir_offset[0], y - (4 - left_idx + 1) * dir_offset[
                                        1]
                                    pos2 = x + (right_idx - 4 + 1) * dir_offset[0], y + (right_idx - 4 + 1) * \
                                           dir_offset[1]
                                    cnt = self.is_it_real_3(pos1, dir_index, mine) + self.is_it_real_3(pos2, dir_index,
                                                                                                       mine)
                                    if cnt <= 1:
                                        count[STHREE] += 1
                                    else:
                                        count[THREE] += 1
                                else:
                                    count[THREE] += 1
                            else:  # PXMMMXP
                                count[STHREE] += 1
                        elif left_empty or right_empty:  # PMMMX, XMMMP
                            count[STHREE] += 1

                # Chong Four: MMXMM, only check right direction
                # Live Three: XMXMMX, XMMXMX the two types can both exist
                # Sleep Three: PMXMMX, XMXMMP, PMMXMX, XMMXMP
                # Live Two: XMMX
                # Sleep Two: PMMX, XMMP
                if m_range == 2:
                    if True:
                        left_empty = right_empty = False
                        left_three = right_three = False
                        if line[left_idx - 1] == empty:
                            if line[left_idx - 2] == mine:
                                if RECORD:
                                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir_offset)
                                if line[left_idx - 3] == empty:
                                    if line[right_idx + 1] == empty:  # XMXMMX
                                        if check3:
                                            pos1 = x - (4 - left_idx + 1) * dir_offset[0], y - (4 - left_idx + 1) * \
                                                   dir_offset[1]
                                            pos2 = x + (right_idx - 4 + 1) * dir_offset[0], y + (right_idx - 4 + 1) * \
                                                   dir_offset[1]
                                            pos3 = x - (4 - left_idx + 3) * dir_offset[0], y - (4 - left_idx + 3) * \
                                                   dir_offset[1]
                                            cnt = self.is_it_real_3(pos1, dir_index, mine) + self.is_it_real_3(pos2,
                                                                                                               dir_index,
                                                                                                               mine) + self.is_it_real_3(
                                                pos3, dir_index, mine)
                                            if cnt <= 2:
                                                count[STHREE] += 1
                                            else:
                                                count[THREE] += 1
                                        else:
                                            count[THREE] += 1

                                    else:  # XMXMMP
                                        count[STHREE] += 1
                                    left_three = True
                                elif line[left_idx - 3] == opponent:
                                    if line[right_idx + 1] == empty:
                                        count[STHREE] += 1
                                        left_three = True

                            left_empty = True

                        if line[right_idx + 1] == empty:
                            if True:
                                if line[right_idx + 2] == mine:
                                    if True:
                                        if line[right_idx + 3] == mine:  # MMXMM
                                            if RECORD:
                                                setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index,
                                                          dir_offset)
                                            if s4:
                                                pos = x + (right_idx - 4 + 1) * dir_offset[0], y + (right_idx - 4 + 1) * \
                                                      dir_offset[1]
                                                count[SFOUR] += self.is_it_real_s4(pos, dir_index, mine)
                                            else:
                                                count[SFOUR] += 1
                                            right_three = True
                                        elif line[right_idx + 3] == empty:
                                            if left_empty:  # XMMXMX
                                                if check3:
                                                    pos1 = x - (4 - left_idx + 1) * dir_offset[0], y - (
                                                                4 - left_idx + 1) * dir_offset[1]
                                                    pos2 = x + (right_idx - 4 + 1) * dir_offset[0], y + (
                                                                right_idx - 4 + 1) * dir_offset[1]
                                                    pos3 = x + (right_idx - 4 + 3) * dir_offset[0], y + (
                                                                right_idx - 4 + 3) * dir_offset[1]
                                                    cnt = self.is_it_real_3(pos1, dir_index, mine) + self.is_it_real_3(
                                                        pos2, dir_index, mine) + self.is_it_real_3(pos3, dir_index,
                                                                                                   mine)
                                                    # print(cnt)

                                                    if cnt <= 2:
                                                        count[STHREE] += 1
                                                    else:
                                                        count[THREE] += 1
                                                else:
                                                    count[THREE] += 1
                                            else:  # PMMXMX
                                                count[STHREE] += 1
                                            right_three = True
                                        elif left_empty:  # XMMXMP
                                            count[STHREE] += 1
                                            right_three = True

                                right_empty = True

                        if left_three or right_three:
                            pass
                        elif left_empty and right_empty:  # XMMX
                            # print("yeah")
                            count[TWO] += 1
                        elif left_empty or right_empty:  # PMMX, XMMP
                            count[STWO] += 1

                # Live Two: XMXMX, XMXXMX only check right direction
                # Sleep Two: PMXMX, XMXMP
                if m_range == 1:
                    if True:
                        left_empty = right_empty = False
                        if line[left_idx - 1] == empty:
                            if line[left_idx - 2] == mine:
                                if line[left_idx - 3] == empty:
                                    if line[right_idx + 1] == opponent:  # XMXMP
                                        count[STWO] += 1
                            left_empty = True

                        if line[right_idx + 1] == empty:
                            if line[right_idx + 2] == mine:
                                if line[right_idx + 3] == empty:
                                    if left_empty:  # XMXMX
                                        count[TWO] += 1
                                    else:  # PMXMX
                                        count[STWO] += 1
                            elif line[right_idx + 2] == empty:
                                if line[right_idx + 3] == mine and line[right_idx + 4] == empty:  # XMXXMX
                                    count[TWO] += 1
                # print(count)
                return 0

    def grid_assess_mine(self, man):  # 对现有grid的assess，返回现局势man的得分
        grid = self.grid
        self.record = [[[0, 0, 0, 0] for x in range(BOARD_ORDER)] for y in range(BOARD_ORDER)]

        self.mcount = [0] * 8
        self.ocount = [0] * 8
        # mine,opponent -> 1/2
        mine = man
        opponent = GRID_BLACK + GRID_WHITE - man
        # 对棋盘每个位置的每个方向都看了棋形
        for x in range(BOARD_ORDER):
            for y in range(BOARD_ORDER):
                for i in range(4):
                    if ((grid[y][x] != GRID_NULL) and (self.record[y][x][i] == 0)):
                        if grid[y][x] == mine:
                            # print(x,y,i,end='\t')
                            self.analysisLine(grid, x, y, i, [SPEED_X[i], SPEED_Y[i]], mine, opponent, self.mcount)

                        else:
                            # print('#',x,y,i,end='\t')
                            self.analysisLine(grid, x, y, i, [SPEED_X[i], SPEED_Y[i]], opponent, mine, self.ocount,
                                              True, False, False)
        # 通过count算mScore,oScore

        self.mScore, self.oScore = self.getPointScore_mine(self.mcount, self.ocount, man)
        # print((mScore,'  ',oScore))
        return (self.mScore - self.oScore)

    def grid_assess_oppo(self, man):  # 对现有grid的assess，返回现局势man的得分
        grid = self.grid
        self.record = [[[0, 0, 0, 0] for x in range(BOARD_ORDER)] for y in range(BOARD_ORDER)]

        self.mcount = [0] * 8
        self.ocount = [0] * 8
        # mine,opponent -> 1/2
        mine = man
        opponent = GRID_BLACK + GRID_WHITE - man
        # 对棋盘每个位置的每个方向都看了棋形
        for x in range(BOARD_ORDER):
            for y in range(BOARD_ORDER):
                for i in range(4):
                    if ((grid[y][x] != GRID_NULL) and (self.record[y][x][i] == 0)):
                        if grid[y][x] == mine:
                            # print(x,y,i,end='\t')
                            self.analysisLine(grid, x, y, i, [SPEED_X[i], SPEED_Y[i]], mine, opponent, self.mcount)

                        else:
                            # print('#',x,y,i,end='\t')
                            self.analysisLine(grid, x, y, i, [SPEED_X[i], SPEED_Y[i]], opponent, mine, self.ocount,
                                              True, False, False)
        # 通过count算mScore,oScore

        self.mScore, self.oScore = self.getPointScore_oppo(self.mcount, self.ocount, man)
        # print((mScore,'  ',oScore))
        return (self.mScore - self.oScore)

    def FindBestChess(self, man):  # man->0/1,将要落子的人
        self.next_x, self.next_y = -1, -1
        maxScore = -WIN_SCORE * 5
        # the first step
        if self.color == GRID_BLACK:

            if (self.roundNum == 1):
                for step in self.FirstStepList:
                    if (abs(step[0] - self.newestOppoStep[0]) + abs(step[1] - self.newestOppoStep[1]) == 1) and (
                            self.grid[step[1]][step[0]] == GRID_NULL):
                        # print("FIND!!")
                        return (step)
        else:  # ai执白棋
            print(self.roundNum)
            if (self.roundNum == 1):
                for x in range(BOARD_ORDER):
                    for y in range(BOARD_ORDER):
                        if ((abs(x - self.newestOppoStep[0]) == 1) and (abs(y - self.newestOppoStep[1]) == 1) and (
                                self.grid[y][y] == GRID_NULL)):
                            print("FIND!!")
                            return ((x, y))

        for (x, y) in (RT_deep_search(self.grid)):  # get surround check point
            # 对每一个可行点 先假装下我方算个分 再假装下对方算分 最后两个分数加权相加 得到位置的总分
            # print(x,"",y,end='\t')
            self.grid[y][x] = man
            score_m = self.grid_assess_mine(man)
            # if ((((x==13)and(y==7))or((x==14)and(y==8)))and(self.roundNum>=25)):
            #     print('############')
            #     print(x,"",y,'\t',score_m)
            #     print('mScore=',self.mScore)
            #     print('oScore=',self.oScore)
            #     print('mcount=',self.mcount)
            #     print('ocount=',self.ocount)
            oppo = GRID_WHITE + GRID_BLACK - man
            self.grid[y][x] = oppo
            score_o = self.grid_assess_oppo(oppo)
            # if ((((x==13)and(y==7))or((x==14)and(y==8)))and(self.roundNum>=25)):
            #     print('----------')
            #     print(x,"",y,'\t',score_m)
            #     print('mScore=',self.mScore)
            #     print('oScore=',self.oScore)
            #     print('mcount=',self.mcount)
            #     print('ocount=',self.ocount)
            #     print('############')
            self.grid[y][x] = GRID_NULL
            # print(score_m,score_o)
            score = score_m + score_o
            if score > maxScore:
                maxScore = score
                self.next_x, self.next_y = x, y

        return self.next_x, self.next_y

    def mouse_down(self, mx, my, scr):  # 鼠标位置->落子坐标 输赢->字幕反馈 只管玩家
        if self.sysStat == 1:
            return
        gx = int((mx - self.x0 - BOARD_X0) / BOARD_SIZE + 0.5)
        gy = int((my - self.y0 - BOARD_Y0) / BOARD_SIZE + 0.5)

        if 0 <= gx < BOARD_ORDER and 0 <= gy < BOARD_ORDER:
            if self.grid[gy][gx] == GRID_NULL:  # 如果落子成功
                # 储存更新对手落子信息
                self.roundNum += 1
                self.turn = self.playerColor
                self.stepGrid[gy][gx] = self.roundNum
                self.grid[gy][gx] = self.playerColor
                self.newestChessPos = [gx, gy]
                self.newestOppoStep = (gx, gy)
                self.draw(scr)
                pygame.display.update()
                self.AI_move(scr)  # AI核心
                if is_five(self.grid, gx, gy, self.playerColor):  # if 对手获胜
                    # print(gx,gy,self.playerColor,is_five(self.grid,gx,gy,self.playerColor ))
                    self.winner = self.playerColor
                    self.sysStat = 1
                    print(OPPO_NAME, 'WIN!!!')
                    return

        return

    def AI_move(self, scr):
        mx, my = self.FindBestChess(self.color)  # find highest point
        self.roundNum += 1
        self.turn = self.color
        self.stepGrid[my][mx] = self.roundNum
        self.grid[my][mx] = self.color
        self.newestChessPos = [mx, my]
        self.draw(scr)
        pygame.display.update()
        if is_five(self.grid, mx, my, self.color):
            self.winner = self.color
            self.sysStat = 1
            print(SELF_NAME, 'WIN!!!')

        # print('round:',self.roundNum)
        # print('------------------------')
        return

    def eventkey(self, key):  # 是否隐藏value
        if key == pygame.K_RETURN and self.sysStat == 1:
            self.grid_init()
            self.sysStat = 0
            self.roundNum = 0
            self.turn = GRID_BLACK
            self.newestChessPos = [-5, -5]
            if self.color == GRID_BLACK:
                m = BOARD_ORDER // 2
                self.grid[m][m] = GRID_BLACK
        return

    def mouse_down_before_start(self, mx, my, scr):
        if mx > SCREEN_WIDTH // 2:  # ai->black
            self.FirstStepList = [[8, 8], [8, 9], [8, 10], [9, 8], [9, 10], [10, 8], [10, 9],
                                  [10, 10]]  # 当AI执黑时，记录黑棋开局第二子可下位置，用于帮助AI下第二子
            self.newestOppoStep = [-1, -1]  # 当AI执黑时，记录白棋最新走向，只用于帮助AI开局下第二子
            self.WHITE_PLAYER_NAME, self.BLACK_PLAYER_NAME = OPPO_NAME, SELF_NAME
            self.black_pos_x, self.black_pos_y = SELF_POS
            self.white_pos_x, self.white_pos_y = OPPO_POS
            self.playerColor, self.color = GRID_WHITE, GRID_BLACK
            m = BOARD_ORDER // 2
            self.grid[m][m] = GRID_BLACK  # 中间落子
            print('ai->black')
        else:  # ai->white
            self.WHITE_PLAYER_NAME, self.BLACK_PLAYER_NAME = SELF_NAME, OPPO_NAME
            self.black_pos_x, self.black_pos_y = OPPO_POS
            self.white_pos_x, self.white_pos_y = SELF_POS
            self.playerColor, self.color = GRID_BLACK, GRID_WHITE
            print('ai->white')
        return


def RT_draw_choice(scr):
    pygame.draw.rect(scr, (0, 0, 0), (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT), 0)
    pygame.draw.rect(scr, (255, 255, 255), (SCREEN_WIDTH // 2, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT), 0)
    fontStart = pygame.font.Font(None, 56)
    fontChoice = pygame.font.Font(None, 80)
    pic = fontStart.render("Choose what YOU operate:", True, (100, 100, 250))
    scr.blit(pic, (SCREEN_WIDTH // 2 - 250, 50))
    pic = fontChoice.render("BLACK", True, (250, 150, 150))
    scr.blit(pic, (SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2))
    pic = fontChoice.render("WHITE", True, (250, 150, 150))
    scr.blit(pic, (SCREEN_WIDTH * 3 // 4 - 100, SCREEN_HEIGHT // 2))


pygame.init()  # pygame初始化
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 生成屏幕对象->screen

# 加载图片(title,白子,黑子)
fPic = pygame.image.load('face01.bmp')
fPic.set_colorkey((0, 0, 0))
wPic = pygame.image.load('WCMan.bmp')
wPic.set_colorkey((255, 0, 0))
bPic = pygame.image.load('BCMan.bmp')
bPic.set_colorkey((255, 0, 0))

IMG_LEN = 30
SELF_POS, OPPO_POS = (729, 498), (731, 609)
BLACK_POS_X, BLACK_POS_Y = SELF_POS
WHITE_POS_X, WHITE_POS_Y = OPPO_POS
# 生成gobang(类对象)
gobang = CLS_gobang(fPic, bPic, wPic, 30, 80)

start = 0  # 是否正式开始比赛

while start == 0:  # 这个循环让玩家选择操作颜色
    RT_draw_choice(screen)
    for event in pygame.event.get():
        # 关闭窗口的处理
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 其他鼠标键盘事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:  # button=1 -> 按下鼠标左键
                continue
            mx, my = event.pos  # 将按下的坐标储存
            # gobang.prepare_game( mx,my )
            # print(mx,my)
            gobang.mouse_down_before_start(mx, my, screen)
            start = 1
        pygame.display.update()
if gobang.color == GRID_WHITE:
    DEF = 2
gobang.draw_board()  # 绘制board
print('start')
while True:
    # print("0")
    for event in pygame.event.get():
        # 关闭窗口的处理
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 其他鼠标键盘事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:  # button=1 -> 按下鼠标左键
                continue
            mx, my = event.pos  # 将按下的坐标储存
            print(mx, my)
            gobang.mouse_down(mx, my, screen)  # gobang做出"下子"反应

        if event.type == pygame.KEYDOWN:  # 按键反应
            gobang.eventkey(event.key)
    # print("01")

    # 主程序

    gobang.draw(screen)  # 绘图update
    # print("012")
    # 画面重绘，没有这一句，不会有任何显示
    pygame.display.update()
