try:
    from urllib2 import Request, urlopen
    py3 = False
except:
    from urllib.request import Request, urlopen
    py3 = True
import json
from datetime import datetime
import time
import threading
try:
	import Tkinter as tk
except:
	import tkinter as tk

running = False
autoactions_stat = {}

#Get Unravel Server Autoactions
def get_actions():
	def run():
		global autoactions_stat
		temp_dict = {}
		while running == True:
			request = Request(input_getaction.get())
			try:
				if py3 == True:
					response = json.loads(urlopen(request).read().decode('utf-8'))
				else:
					response = json.loads(urlopen(request).read())
				#clear previous result
				text_actionlist.delete("1.0",tk.END)
				text_actionstat.delete("1.0",tk.END)
				status_pagerduty.place_forget()
				#Show Active Autoactions
				result = ''
				for i in range(len(response['active'])):
					action_name = response['active'][i]['name_by_user']
					#result += "Autoaction Name: " + action_name + "\t Status: Active" + "\n"
					temp_dict[action_name] = 'active'
					print("Autoaction Name: " + action_name + "\t Status: Active")
					text_actionlist.insert(tk.END, action_name + "\n")
					text_actionstat.insert(tk.END, "Active" +  "\n")
				#Show Inactive Autoactions
				for i in range(len(response['inactive'])):
					action_name = response['inactive'][i]['name_by_user']
					#result += "Autoaction Name: " + action_name + "\t Status: Inactive" + "\n"
					temp_dict[action_name] = 'inactive'
					print("Autoaction Name: " + action_name + "\t Status: Inactive")
					text_actionlist.insert(tk.END, action_name + "\n")
					text_actionstat.insert(tk.END, "Inactive" +  "\n")
					
			except Exception as e:
				print("No Connection or Invalid address")
				print(e)
				text_actionlist.insert(tk.END,"No Connection or Invalid address")
			
			if running == False:
				break

			if not autoactions_stat:
				autoactions_stat =  temp_dict.copy()
			elif temp_dict != autoactions_stat:
				for item in temp_dict:
					if item not in autoactions_stat or temp_dict[item] != autoactions_stat[item]:
						result += 'Autoaction:' + item + ' status changed '
				print('Not Match, Send Notification to Pagerduty')
				trig_pd(result)
				autoactions_stat = temp_dict.copy()
			time.sleep(5)
			
	thread = threading.Thread(target=run)
	thread.start()
				
#Trigger Pagerduty Event
def trig_pd(des):
	data = json.dumps({
		"routing_key": text_pagerduty.get(),
		"event_action":"trigger",
		"payload":{
			"summary":des,
			"source": "dingo4.unraveldatalab.com",
			"severity":"warning"
		}})
	try:
		req = Request("https://events.pagerduty.com/v2/enqueue", data, {'Content-Type': 'application/json'})
		response = urlopen(req).read()
		print(response)
		if json.loads(response)['status'] == 'success':
			status_pagerduty['text'] = 'success'
			status_pagerduty['bg'] = 'green'
			status_pagerduty.place(x=w-100, y=290)
		else:
			status_pagerduty['text'] = 'fail'
			status_pagerduty['bg'] = 'red'
			status_pagerduty.place(x=w-100, y=290)
	except Exception as e:
		status_pagerduty['text'] = 'fail'
		status_pagerduty['bg'] = 'red'
		status_pagerduty.place(x=w-100, y=290)

def start_monitor():
	global running
	if butt_getaction['text'] == 'Start':
		butt_getaction['text'] = 'Stop'
		running = True
	else:
		butt_getaction['text'] = 'Start'
		running = False
	get_actions()

#Create Root Window with Width, Height, and x, y initial posotion
root = tk.Tk()
root.minsize(500,300)
root.resizable(0,0)
root.title("Unravel API Demo")
w = 600
h = 320
x = 50
y = 50
root.geometry("%dx%d+%d+%d" % (w, h, x, y))

#Create Frame for elements
frame = tk.Frame(root)
frame.pack(fill="both", expand="yes")

#Autoactions Button & Entry
title_getaction = tk.Label(frame, text="Unravel Autoactions API address")
title_getaction.place(x=10,y=0)
input_getaction = tk.Entry(frame,width=49)
input_getaction.insert(0,"http://172.16.1.62:3000/api/v1/autoactions/")
input_getaction.place(x=10,y=20)
butt_getaction = tk.Button(frame, text="Start", command=start_monitor)
butt_getaction.place(x=w-65, y=20)

#Autoactions API Result Textbox
title_actionlist = tk.Label(frame,text="Autoaction Name")
title_actionlist.place(x=10, y=60)
title_actionstat = tk.Label(frame,text="Autoaction Status")
title_actionstat.place(x=450, y=60)
text_actionlist = tk.Text(frame, width=60, height=12)
text_actionlist.place(x=10, y=80)
text_actionstat = tk.Text(frame, width = 20, height = 12)
text_actionstat.place(x=450, y=80)
status_pagerduty = tk.Label(frame)

#Pagerduty Token
title_pagerduty = tk.Label(frame, text="Pagerduty API Key")
title_pagerduty.place(x=10, y=290)
text_pagerduty = tk.Entry(frame, width=30)
text_pagerduty.insert(tk.END, '9492f46cacc3477284e3de569191201e')
text_pagerduty.place(x=135, y=290)
root.mainloop()
