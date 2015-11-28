#!/usr/bin/python
import web
import subprocess
import re
import time

urls = (
	'/', 'index',
	'/app.py', 'ajax'
)

app = web.application(urls, globals())

class ajax:
	def GET(self):
                output = subprocess.check_output("grep MemTotal /proc/meminfo", shell = True)
                MemTotal = re.search('(\d+)', output).group(1)
                output = subprocess.check_output("grep MemFree /proc/meminfo", shell = True)
                MemFree = re.search('(\d+)', output).group(1)
                output = subprocess.check_output("free | grep Swap", shell = True)
                match = re.search('(\d+)\s+\d+\s+(\d+)', output)
                SwapTotal = match.group(1)
                SwapFree = match.group(2)
                output = subprocess.check_output("df | grep rootfs", shell = True)
                match = re.search('(\d+)\s+\d+\s+(\d+)', output)
                DiskTotal = match.group(1)
                DiskFree = match.group(2)
                output = subprocess.check_output("cat /proc/loadavg", shell = True)
                Processor = re.search('^\d+\.\d+\s+\d+\.\d+\s+(\d+)', output).group(1)
                output = subprocess.check_output("cat /proc/uptime", shell = True)
                Uptime = re.search('^(\d+)', output).group(1)
                output = subprocess.check_output("ps aux | wc -l", shell = True)
                Processes = int(re.search('^(\d+)', output).group(1)) - 1
                output = subprocess.check_output("ifconfig wlan0 | grep 'inet addr'", shell = True)
                Address = re.search('inet addr:(\d+\.\d+\.\d+\.\d+)', output).group(1)
		return '''{
  "memory": "''' + str(int(float(MemFree) / float(MemTotal) * 100)) + '''",
  "swap": "''' + str(int(float(SwapFree) / float(SwapTotal) * 100)) + '''",
  "disk": "''' + str(int(float(DiskFree) / float(DiskTotal) * 100)) + '''",
  "processor": "''' + str(Processor) + '''",
  "date": "''' + time.strftime("%b %d %Y %H:%M:%S") + '''",
  "uptime": "up ''' + Uptime + ''' seconds",
  "processes": "''' + str(Processes) + '''",
  "address": "''' + Address + '''"
}'''

class index:
	def GET(self):
		return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title></title>
<style type="text/css">
body
{
  margin: 0px;
  padding: 0px;
}
body > div
{
  display: table;
  position: absolute;
  height: 100%;
  width: 100%;
  background: linear-gradient(to top, #fefca0, #f1da36);
}
body > div > div
{
  display: table-cell;
  vertical-align: middle;
}
body > div > div > div
{
  margin: auto;
  width: 80%;
  border: 2px solid gray;
  border-radius: 20px;
  background: #ffffff;
  padding: 20px;
}
body > div > div > div > div
{
  display: table;
  margin: auto;
  border-spacing: 20px;
}
body > div > div > div > div > div
{
  display: table-row;
}
body > div > div > div > div > div > div
{
  display: table-cell;
}
.param
{
  border: 1px solid #c0c0c0;
  padding: 5px 10px;
  background: linear-gradient(to top, #fefca0, #f1da36);  
  font: bold 11px tahoma;
}
.circle
{
  border: 1px solid #c0c0c0;
  border-radius: 5px;
}
.value
{
  border: 1px solid #c0c0c0;
  padding: 5px 10px;
  text-align: right;
  font: 11px tahoma;
}
.refresh
{
  text-align: right;
  font: 10px tahoma;
}
.refresh > a
{
  color: #0000ff;
}
</style>
<script type="text/javascript" src="http://code.jquery.com/jquery.min.js"></script>
<script type="text/javascript">
function draw_circle(canvas, percent)
{
  var context = $(canvas)[0].getContext("2d");

  context.fillStyle = "white";
  context.fillRect(0, 0, $(canvas)[0].width, $(canvas)[0].height);

  context.beginPath();
  context.arc(100, 100, 50, -0.5 * Math.PI, 2 * Math.PI / 100 * percent - 0.5 * Math.PI);
  context.fillStyle = "black";
  context.lineWidth = 8;
  context.stroke();

  context.font = "30px Tahoma";
  context.textAlign = "center";
  context.fillText(percent + "%", $(canvas)[0].width / 2, $(canvas)[0].height / 2 + 10);
}
function refresh()
{
  $.ajax({dataType: "json", url: "app.py", success: function(data)
  {
    draw_circle("#canvas1", data.memory);
    draw_circle("#canvas2", data.swap);
    draw_circle("#canvas3", data.disk);
    draw_circle("#canvas4", data.processor);

    $("#param1").html(data.date);
    $("#param2").html(data.uptime);
    $("#param3").html(data.processes);
    $("#param4").html(data.address);
  }});
}
$(document).ready(function()
{
  refresh();
});
</script>
</head>
<body>
<div>
  <div>
    <div>
      <div>
        <div>
          <div class="param">Free Memory:</div>
          <div class="param">Free Swapspace:</div>
          <div class="param">Free Diskspace:</div>
          <div class="param">CPU Usage:</div>
        </div>
        <div>
          <div class="circle"><canvas width="200" height="200" id="canvas1"></canvas></div>
          <div class="circle"><canvas width="200" height="200" id="canvas2"></canvas></div>
          <div class="circle"><canvas width="200" height="200" id="canvas3"></canvas></div>
          <div class="circle"><canvas width="200" height="200" id="canvas4"></canvas></div>
        </div>
        <div>
          <div class="param">Date:</div>
          <div class="param">Uptime:</div>
          <div class="param">Processes:</div>
          <div class="param">IP Address:</div>
        </div>
        <div>
          <div id="param1" class="value"></div>
          <div id="param2" class="value"></div>
          <div id="param3" class="value"></div>
          <div id="param4" class="value"></div>
        </div>
        <div>
          <div></div>
          <div></div>
          <div></div>
          <div class="refresh"><a href="javascript://" onclick="refresh()">refresh</a></div>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>'''

if __name__ == "__main__":
	app.run()
