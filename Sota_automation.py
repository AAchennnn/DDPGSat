from pywinauto import Application
import time
from pywinauto.mouse import click
from pywinauto.keyboard import send_keys
import pyautogui

class SOTASimulation:
    def SOTA_calculate(self, start_date, start_time, duration, n):
        '-n 指的是调用次数，用来定义文件夹 要是字符串类型'
        # SOTA路径
        app_path = r"C:\Program Files\AGI\SOTA\bin\SpaceObjectThreatAssessment.exe"
        app = Application().start(app_path)
        # 等待程序完全启动
        time.sleep(5)

        # 获取应用程序窗口的句柄（可以根据程序窗口的标题来识别）
        main_window = app.window(title_re=".*SOTA.*")

        # # 捕捉窗口中的某些元素，例如按钮、输入框
        # main_window.print_control_identifiers()
        # 获取日期时间控件
        date_picker = main_window.child_window(auto_id="txtDate", control_type="System.Windows.Forms.TextBox")
        time_picker = main_window.child_window(auto_id="txtTime", control_type="System.Windows.Forms.TextBox")

        # 设置新的日期
        date_picker.set_text(start_date)
        time_picker.set_text(start_time)

        # duration时长更新
        duration_picker = main_window.child_window(auto_id="txtDuration", control_type="System.Windows.Forms.TextBox")
        duration_picker.set_text(duration)

        # duration单位更新
        hour_combobox = main_window.child_window(title="Hours", auto_id="cmbDurationUnits",
                                                 control_type="System.Windows.Forms.ComboBox")
        hour_combobox.select("Hours")
        '''---------添加追逐卫星------------'''
        #打开添加 Chaser Vehicles
        submit_button = main_window.child_window(title="Add Vehicles", found_index=0,auto_id="btnAddItems",
                                                 control_type="System.Windows.Forms.Button")
        submit_button.click_input()     # 点击按钮
        time.sleep(1)

        # 定位到 弹出窗口 选择From stK
        sub_window_addVehiclesForm = app.window(title_re=".*AddVehiclesForm.*")
        time.sleep(1)
        send_keys("{DOWN}{DOWN}")
       #取消掉全选
        ccc=sub_window_addVehiclesForm.child_window(title="Available STK Satellites", auto_id="cbCheckAllAvailable", control_type="System.Windows.Forms.CheckBox")
        ccc.click_input()
       #选择前五个为我的追逐星
        for i in range(5):
            send_keys("{DOWN}{SPACE}")  # 移动到第一颗卫星并选中
        #选中添加
        add_button = sub_window_addVehiclesForm.child_window(title="ADD VEHICLES", auto_id="btnAddItems",
                                                             control_type="System.Windows.Forms.Button")
        add_button.click_input()
        '''---------添加逃逸卫星------------'''
        submit_button2 = main_window.child_window(title="Add Vehicles", found_index=1,auto_id="btnAddItems", control_type="System.Windows.Forms.Button")
        submit_button2.click_input()     # 点击按钮
        time.sleep(1)
        sub_window_addVehiclesForm2 = app.window(title_re=".*AddVehiclesForm.*")
        time.sleep(1)
        send_keys("{DOWN}{DOWN}")
       # 取消掉全选
        ccc1 = sub_window_addVehiclesForm.child_window(title="Available STK Satellites", auto_id="cbCheckAllAvailable", control_type="System.Windows.Forms.CheckBox")
        ccc.click_input()
       # 选择第六个个为我的追逐星
        for i in range(6):
            send_keys("{DOWN}")  # 移动到第一颗卫星并选中
        send_keys("{SPACE}")
        # 选中添加
        add_button = sub_window_addVehiclesForm.child_window(title="ADD VEHICLES", auto_id="btnAddItems", control_type="System.Windows.Forms.Button")
        add_button.click_input()
        #进行计算
        calculate_button = main_window.child_window(title="Calculate", auto_id="btnCompute", control_type="System.Windows.Forms.Button")
        calculate_button.click_input()
#把生成的星历文件导出
        time.sleep(5)
        # View = main_window.child_window(auto_id="dgvResultsGridView", control_type="System.Windows.Forms.DataGridView")
        #for row in View.children():
        main_window_now = app.window(title_re=".*SOTA.*")
        #在这加一个循环 判断是否有result view 判断到就推出 进行下一步
        #time.sleep(60) ###
        #while(1):
        result_view = main_window_now.child_window(auto_id="ResultsTabControl", control_type="AGI.SSA.SpaceObjectThreatAssessment.Ui.ResultsTabControl")
        grid = result_view.child_window(auto_id="dgvResultsGridView", control_type="System.Windows.Forms.DataGridView")
        #while(1):
             #if grid.exists() == 1:
                #break
        time.sleep(3)
        #rect = grid.rectangle()
        #row_height = 30
        #row_y =int(rect.top + 0.5 * row_height)
        for i in range(5):
            while(1):
                if grid.exists() == 1:
                    break
            grid.click_input()
            time.sleep(3)
            pyautogui.move(0, -110+55*i)  # x 不变，y 减小，向上移动
            k = n+'_'+str(i)
            pyautogui.rightClick()
            pyautogui.press('right')  # 按一次下箭头
            pyautogui.press('enter')  # 按下回车键

            #利用导航树来定位文件夹
            dlg = app.window(title_re=".*浏览文件夹.*")
            tree = dlg.TreeView
            target_path = ["此电脑", 'Data (D:)', 'Datas_cxy']
            current_node = tree.roots()
            current_node = current_node[0] #指向此电脑
            #print(f"正在定位: {'桌面'}")  # 先定位电脑
            # 展开当前节点（如果尚未展开）
            current_node.expand()  # 把桌面展开
            dlg.wait("ready", timeout=2)  # 等待展开动画
            # 精确查找子节点（支持部分匹配）
            children = [child.text() for child in current_node.children()]  # 搜寻电脑下面的子文件夹
            #print(f"可用子节点: {children}")
            for folder in target_path:
                match = None
                for child in current_node.children():
                    if folder in child.text():  # 部分匹配逻辑
                        match = child
                        break
                if not match:
                    raise Exception(f"未找到节点: {folder}")
                current_node = match
                current_node.ensure_visible()  # 滚动到可视区域
                #print(f"正在定位: {folder}")  # 先定位电脑
                # 展开当前节点（如果尚未展开）
                current_node.expand()  # 把电脑展开
                app.Dialog.wait("ready", timeout=2)  # 等待展开动画
                # 精确查找子节点（支持部分匹配）
                children = [child.text() for child in current_node.children()]  # 搜寻电脑下面的子文件夹
                #print(f"可用子节点: {children}")
                # 查找匹配项（处理可能的名称差异）
            # 最终选择操作

            current_node.select()
            time.sleep(3)
            #current_node.click_input(button="left") #double=True)
            #time.sleep(10)
            new_button = dlg.child_window(title="新建文件夹(&M)", class_name="Button")
            new_button.click_input(button='left')
            time.sleep(3)
            pyautogui.typewrite(k)
            time.sleep(2)
            pyautogui.press('enter')  # 按下回车键
            time.sleep(3)
            pyautogui.press('enter')  # 按下回车键
            # pyautogui.press('enter')  # 按下回车键
            #pyautogui.press('left')  # 放在新建文件夹中
            #pyautogui.press('enter')  # 按下回车键
            #pyautogui.typewrite(k)
            #time.sleep(2)
            #pyautogui.press('enter')  # 按下回车键
            #time.sleep(3)
            #pyautogui.press('enter')  # 按下回车键
        button_close = main_window.child_window(auto_id="btnClose", control_type="System.Windows.Forms.Button")
        while(1):
            if button_close.exists():
                break
        button_close.click_input()





