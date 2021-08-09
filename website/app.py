import numpy as np 

amplitude = 1
period = 10
#time = np.arange(1,int(2*period))
#wave = amplitude*np.sin((2*(np.pi)/period)*time)


from flask import Flask, render_template, request

app = Flask(__name__)
#amplitude = 0
#period = 0

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        amplitude = int(request.form.get("amplitude"))
        period = int(request.form.get("period"))
        time = np.arange(1,int(2*period))
        wave = amplitude*np.sin((2*(np.pi)/period)*time)
        labels = list(time)
        values = list(wave)
        waveParams = [amplitude, period]
    else:
        labels = []
        values = []
        waveParams = [0, 0]
    #return render_template("graph.html", period=period)
    return render_template("graph.html", labels=labels, values=values, waveParams=waveParams)

