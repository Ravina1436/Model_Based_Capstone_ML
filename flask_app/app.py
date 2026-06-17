from flask import Flask, request, render_template
import pickle
import pandas as pd

app = Flask(__name__)

# 🔹 Load model and scaler
model = pickle.load(open("rf_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# 🔹 Load dataset
df = pd.read_csv("final_model_ready_dataset.csv")

# 🔹 Fix data types
df["Renewable_Consumption_Pct"] = pd.to_numeric(
    df["Renewable_Consumption_Pct"], errors="coerce"
)

df = df.dropna()

# 🔹 Common values
def get_common():
    countries = sorted(df["country_name"].unique())
    years = sorted(df["year"].unique())
    return countries, years


# 🔹 Home Page
@app.route("/")
def home():
    countries, years = get_common()

    return render_template(
        "index.html",
        countries=countries,
        years=years,
        selected_country=None,
        selected_year=None
    )


# 🔹 DATASET MODE
@app.route("/predict", methods=["POST"])
def predict():
    try:
        country = request.form["country"]
        year = int(request.form["year"])

        countries, years = get_common()

        row = df[(df["country_name"] == country) & (df["year"] == year)]

        if row.empty:
            return render_template(
                "index.html",
                countries=countries,
                years=years,
                selected_country=country,
                selected_year=year,
                prediction_text="No data available for selected country/year"
            )

        renewable = float(row["Renewable_Consumption_Pct"].values[0])
        carbon = float(row["CO2_Intensity"].values[0])
        gdp = float(row["CO2_per_GDP_PPP"].values[0])
        methane = float(row["Methane_CO2e"].values[0])
        n2o = float(row["N2O_CO2e"].values[0])

        data = [[year, renewable, carbon, gdp, methane, n2o]]
        final_input = scaler.transform(data)
        prediction = model.predict(final_input)

        return render_template(
            "index.html",
            countries=countries,
            years=years,
            selected_country=country,
            selected_year=year,
            prediction_text=f"Dataset Prediction: {round(prediction[0], 2)}"
        )

    except Exception as e:
        countries, years = get_common()
        return render_template(
            "index.html",
            countries=countries,
            years=years,
            prediction_text=f"Error: {str(e)}"
        )


# 🔹 MANUAL MODE
@app.route("/manual_predict", methods=["POST"])
def manual_predict():
    try:
        year = float(request.form["year"] or 0)
        renewable = float(request.form["renewable"] or 0)
        carbon = float(request.form["carbon"] or 0)
        gdp = float(request.form["gdp"] or 0)
        methane = float(request.form["methane"] or 0)
        n2o = float(request.form["n2o"] or 0)

        data = [[year, renewable, carbon, gdp, methane, n2o]]
        final_input = scaler.transform(data)
        prediction = model.predict(final_input)

        countries, years = get_common()

        return render_template(
            "index.html",
            countries=countries,
            years=years,
            prediction_text=f"Manual Prediction: {round(prediction[0], 2)}"
        )

    except Exception as e:
        countries, years = get_common()
        return render_template(
            "index.html",
            countries=countries,
            years=years,
            prediction_text=f"Error: {str(e)}"
        )


# 🔹 FUTURE MODE
@app.route("/future_predict", methods=["POST"])
def future_predict():
    try:
        future_year = int(request.form["year"])

        last_year = df["year"].max()
        last_data = df[df["year"] == last_year].mean(numeric_only=True)

        year_diff = future_year - last_year

        renewable = last_data["Renewable_Consumption_Pct"] + (year_diff * 0.5)
        carbon = last_data["CO2_Intensity"] - (year_diff * 0.2)
        gdp = last_data["CO2_per_GDP_PPP"] + (year_diff * 1)
        methane = last_data["Methane_CO2e"]
        n2o = last_data["N2O_CO2e"]

        data = [[future_year, renewable, carbon, gdp, methane, n2o]]
        final_input = scaler.transform(data)
        prediction = model.predict(final_input)

        countries, years = get_common()

        return render_template(
            "index.html",
            countries=countries,
            years=years,
            prediction_text=f"Future Prediction ({future_year}): {round(prediction[0], 2)}"
        )

    except Exception as e:
        countries, years = get_common()
        return render_template(
            "index.html",
            countries=countries,
            years=years,
            prediction_text=f"Error: {str(e)}"
        )


# 🔹 Run App
if __name__ == "__main__":
    app.run(debug=True)