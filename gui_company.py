from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from newtest import Company
from datetime import *
from dateutil import relativedelta as delta
import os


def date_diff(date_start):
    return delta.relativedelta(datetime.now().date(), datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%S").date())


def check_inn(str_inn):
    quot10_arr = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    quot12_1_arr = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    quot12_2_arr = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    control_sum, control_sum1, control_sum2 = 0, 0, 0
    try:
        if len(str_inn) == 10:
            for idx in range(9): control_sum += int(str_inn[idx]) * quot10_arr[idx]
            control_sum %= 11
            if (control_sum if control_sum < 10 else 0) == int(str_inn[9]): return True
        if len(str_inn) == 12:
            for idx in range(10): control_sum1 += int(str_inn[idx]) * quot12_1_arr[idx]
            control_sum1 %= 11
            for idx in range(11): control_sum2 += int(str_inn[idx]) * quot12_2_arr[idx]
            control_sum2 %= 11
            if (control_sum1 if control_sum1<10 else 0) == int(str_inn[10]) and \
                (control_sum2 if control_sum2<10 else 0) == int(str_inn[11]): return True
        return False
    except:  # не удалось получить числа числа
        return False


def show_main_window():

    def btn_run_click(event=None):
        if not text_inn.get().isdigit() or not check_inn(text_inn.get()):
            messagebox.showerror(title="Ошибка", message="Неверно введен ИНН")
            return
        print(text_inn.get())
        window.destroy()
        show_company_info_window(text_inn.get())

    def on_write(*args):
        s = text_inn.get()
        if len(s) > 12: text_inn.set(s[:12])

    window = Tk()
    window.title("Поиск информации об организациях")
    window.geometry(f"520x100+{window.winfo_screenwidth() // 2 - 260}+{window.winfo_screenheight() // 2 - 50}")
    window.resizable(width=0, height=0)
    label_inn = Label(window, text="Введите ИНН организации:", width=25, height=2, font=("Courier", 14))
    label_inn.grid(row=0, column=0)
    text_inn = StringVar()
    text_inn.trace_variable("w", on_write)
    entry_inn = Entry(window, width=20, font=("Courier", 14), textvariable=text_inn)
    entry_inn.bind('<Return>', btn_run_click)
    entry_inn.grid(row=0, column=1)
    entry_inn.focus_set()
    button_run = Button(window, text="Запуск", width=7, height=1, font=("Courier", 14), command=btn_run_click)
    button_run.grid(row=1, column=1, sticky="e")
    window.mainloop()


def show_company_info_window(inn):

    def show_bankrupt_messages():
        if os.path.exists(f"{os.getcwd()}\\Сообщения_о_банкротстве_{inn}.rtf"):
            if messagebox.askyesno(title='Предупреждение',
                                   message='Информация была загружена ранее. Загрузить ее повторно?'):
                gang.get_bankrupt_messages(just_check=False)
        else: gang.get_bankrupt_messages(just_check=False)
        try:
            os.startfile(f"{os.getcwd()}\\Сообщения_о_банкротстве_{inn}.rtf")
        except Exception:
            messagebox.showerror(title="Ошибка", message="Не удалось открыть файл")

    def show_pledge_messages():
        if os.path.exists(f"{os.getcwd()}\\Информация_о_залогах_{inn}.rtf"):
            if messagebox.askyesno(title='Предупреждение',
                                   message='Информация была загружена ранее. Загрузить ее повторно?'):
                gang.get_pledges(just_check=False)
                print('ABOBNAYA ABOBA')
        else: gang.get_pledges(just_check=False)
        try:
            os.startfile(f"{os.getcwd()}\\Информация_о_залогах_{inn}.rtf")
        except Exception:
            messagebox.showerror(title="Ошибка", message="Не удалось открыть файл")

    gang = Company(inn)
    gang.get_organization_card()
    gang.get_exec_processes(just_check=True)
    gang.get_bankrupt_messages(just_check=True)
    gang.get_pledges(just_check=True)

    window = Tk()
    window.title("Карточка организации")
    window.geometry(f"1200x800+{window.winfo_screenwidth() // 2 - 600}+{window.winfo_screenheight() // 2 - 400}")

    lbl_name = Label(window, text="Краткое наименование организации: ", font=("Courier", 14))
    lbl_name.grid(row=0, column=0, sticky="w")
    entry_name = Entry(window, font=("Courier", 14), textvariable=StringVar(value=gang.card['shortName']), state="read",
                       width=40)
    entry_name.grid(row=0, column=1, sticky="e")

    lbl_inn = Label(window, text="ИНН организации: ", font=("courier", 14))
    lbl_inn.grid(row=1, column=0, sticky="w")
    entry_inn = Entry(window, font=("Courier", 14), textvariable=StringVar(value=inn), state="read", width=40)
    entry_inn.grid(row=1, column=1, sticky="e")

    lbl_date = Label(window, text="Возраст организации: ", font=("courier", 14))
    lbl_date.grid(row=2, column=0, sticky="w")
    textdate = date_diff(gang.card['registrationDate'])
    textdate = f"полных лет: {textdate.years}, месяцев: {textdate.months}"
    entry_date = Entry(window, font=("courier", 14), textvariable=StringVar(value=textdate), state="read", width=40)
    entry_date.grid(row=2, column=1, sticky="e")

    lbl_status = Label(window, text="Статус: ", font=("courier", 14))
    lbl_status.grid(row=3, column=0, sticky="w")
    entry_status = Entry(window, font=("courier", 14), textvariable=StringVar(value=gang.card['statusInfo']['name']),
                         state="read", width=40)
    entry_status.grid(row=3, column=1, sticky="e")

    lbl_capital = Label(window, text="Уставный капитал: ", font=("courier", 14))
    lbl_capital.grid(row=4, column=0, sticky="w")
    entry_capital = Entry(window, font=("courier", 14), state="read", width=40,
                          textvariable=StringVar(value="{:,.2f}".format(float(gang.card['authorizedCapital']))))
    entry_capital.grid(row=4, column=1, sticky="e")

    lbl_employees = Label(window, text="Среднесписочная численность сотрудников: ", font=("courier", 14))
    lbl_employees.grid(row=5, column=0, sticky="w")
    if not len(gang.card['taxInfos']) or gang.card['taxInfos'][-1]['year'] is None or \
            gang.card['taxInfos'][-1]['employeesCount'] is None:
        text_empl = "информация не найдена"
    else:
        text_empl = "актуально на " + str(gang.card['taxInfos'][-1]['year']) + " год, сотрудников: " + \
                    str(gang.card['taxInfos'][-1]['employeesCount'])
    entry_empl = Entry(window, font=("courier", 14), state="read", width=40, textvariable=StringVar(value=text_empl))
    entry_empl.grid(row=5, column=1, sticky="e")

    lbl_proc_amount = Label(window, text="Незавершенных исполнительных производств: ", font=("courier", 14))
    lbl_proc_amount.grid(row=6, column=0, sticky="w")
    entry_proc_amount = Entry(window, font=("courier", 14), state="read", width=40,
                              textvariable=StringVar(value=str(gang.check_exec_processes)))
    entry_proc_amount.grid(row=6, column=1, sticky="e")

    if gang.check_exec_processes: gang.get_exec_processes(just_check=False)

    lbl_proc_summ = Label(window, text="Оставшаяся сумма к погашению: ", font=("courier", 14))
    lbl_proc_summ.grid(row=7, column=0, sticky="w")

    entry_proc_summ = Entry(window, font=("courier", 14), state="read", width=40,
                            textvariable=StringVar(value=str("{:,.2f}".format(gang.unpaid_money))))
    entry_proc_summ.grid(row=7, column=1, sticky="e")

    lbl_bankrupt_mess = Label(window, text="Сообщения о банкротстве: ", font=("courier", 14))
    lbl_bankrupt_mess.grid(row=8, column=0, sticky="w")
    btn_bankrupt_mess = Button(window, text=("Не найдено" if not gang.check_bankrupt_messages else "Просмотреть"),
                               font=("courier", 14), width=40, state=("active" if gang.check_bankrupt_messages else
                                                                      "disabled"), command=show_bankrupt_messages)
    btn_bankrupt_mess.grid(row=8, column=1, sticky="e")

    lbl_pledge = Label(window, text="Сообщения о залогах: ", font=("courier", 14))
    lbl_pledge.grid(row=9, column=0, sticky="w")
    btn_pledge = Button(window,
                        text=("Не найдено" if not gang.check_pledges_messages
                              else f"Найдено сообщений: {gang.check_pledges_messages}. Просмотреть"),
                        font=("courier", 14), state=("active" if gang.check_pledges_messages else "disabled"),
                        command=show_pledge_messages, width=40)
    btn_pledge.grid(row=9, column=1, sticky="e")

    founders_tree = ttk.Treeview(window)
    columnz = ('Наименование', 'ИНН', 'Статус', 'Исполнительные Производства',
               'Сообщения о банкротстве', 'Сообщения о залогах')
    founders_tree['columns'] = columnz
    founders_tree.column("#0", width=0, minwidth=0)
    founders_tree.heading("#0", text='', anchor=CENTER)
    for i in columnz:
        founders_tree.column(i, anchor=CENTER, width=200)
        founders_tree.heading(i, text=i, anchor=W)
    gang.get_founders()
    all_founders = gang.print_founders()
    i = 0
    while len(all_founders):
        founders_tree.insert(parent='', index='end', iid=i, text=i, values=all_founders.pop())
        i += 1
    founders_tree.grid(row=10, column=0, columnspan=2)

    window.mainloop()


if __name__ == "__main__":
    show_main_window()
    #show_company_info_window("7718979307")
    #show_company_info_window("7734413460")
    #show_company_info_window("0814099824")
