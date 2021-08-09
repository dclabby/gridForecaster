from flask import Flask, render_template, request

app = Flask(__name__)
transactions = []
#transactions = [("2020-08-05", 70.0, "Checking"), ("2020-08-27", 150.0, "Savings"), ("2020-08-13", 15.96, "Checking")] # this is test data - usually the list should be initialized to empty

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        transactions.append(
            (
                request.form.get("date"),
                float(request.form.get("amount")),
                request.form.get("account")
            )
        )
    return render_template("form.html", entries=transactions) # render template sends html code to browser

@app.route("/graph")
def make_graph():
    data = [("01-01-2020", 1597), ("02-01-2020", 1456), ("03-01-2020", 1908), ("04-01-2020", 2205), ("05-01-2020", 1103), ("06-01-2020", 1205), ("07-01-2020", 995), ("08-01-2020", 975)]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return render_template("graph.html", labels=labels, values=values)

@app.route("/transactions")
def show_transactions():
    return render_template("transactions.html", entries=transactions)


if __name__ == '__main__':
    app.run(debug=True) 