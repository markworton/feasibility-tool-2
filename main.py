import streamlit as st
import pandas as pd
from utils.geolocation import get_coordinates
from utils.ninja_api import get_ninja_data

st.set_page_config(page_title="Renewable Feasibility Tool", layout="centered")
st.title("🔋 Renewable Energy Feasibility Tool")

postcode = st.text_input("Enter UK Postcode")
col1, col2 = st.columns(2)
with col1:
    site_input = st.number_input("Site Size", min_value=0.0)
with col2:
    unit = st.selectbox("Unit", ["sqm", "hectares", "acres"])
unit_factors = {"sqm": 1, "hectares": 10000, "acres": 4046.86}
site_size = site_input * unit_factors[unit]

annual_consumption = st.number_input("Annual Energy Consumption (kWh/year)", min_value=0)
export_price = st.number_input("Export Price (p/kWh)", min_value=0.0, value=5.0) / 100  # default 5p/kWh

if st.button("Run Feasibility Check"):
    try:
        lat, lon = get_coordinates(postcode)
        solar_data = get_ninja_data(lat, lon, tech="solar")
        wind_data = get_ninja_data(lat, lon, tech="wind")

        def extract_electricity(data, label):
            try:
                if not data:
                    st.warning(f"No data returned for {label}.")
                    return []
                values = list(data.values())
                sample = values[0]
                if isinstance(sample, dict) and "electricity" in sample:
                    return [v["electricity"] for v in values]
                elif isinstance(sample, (float, int)):
                    return list(values)
                else:
                    st.warning(f"Unexpected format in {label}: {type(sample)}")
                    st.json(sample)
                    return []
            except Exception as ex:
                st.error(f"Failed to extract {label} data: {ex}")
                return []

        solar_raw = solar_data.get("data", {})
        wind_raw = wind_data.get("data", {})

        solar_df = pd.DataFrame({"electricity": extract_electricity(solar_raw, "solar")})
        wind_df = pd.DataFrame({"electricity": extract_electricity(wind_raw, "wind")})

        st.success("Assessment Complete!")

        st.header("☀️ Solar Feasibility")
        if "electricity" not in solar_df.columns or solar_df.empty:
            st.error("❌ Solar data missing 'electricity' column. Check API response.")
        else:
            solar_yield = solar_df["electricity"].sum()
            st.metric("Annual Solar Yield (kWh/kWp)", f"{solar_yield:.0f}")
            solar_capex = 1000
            solar_kwp = min(site_size / 10, annual_consumption / solar_yield)
            solar_cost = solar_kwp * solar_capex
            solar_generated = solar_yield * solar_kwp
            solar_used = min(solar_generated, annual_consumption)
            solar_excess = max(0, solar_generated - annual_consumption)
            solar_savings = solar_used * 0.20 + solar_excess * export_price
            solar_payback = solar_cost / solar_savings if solar_savings > 0 else None

            st.write(f"**Estimated System Size:** {solar_kwp:.1f} kWp")
            st.write(f"**CapEx:** £{solar_cost:,.0f}")
            st.write(f"**Annual Savings:** £{solar_savings:,.0f}")
            st.write(f"**Estimated Payback:** {solar_payback:.1f} years" if solar_payback else "N/A")

        st.divider()
        st.header("💨 Wind Feasibility")
        if "electricity" not in wind_df.columns or wind_df.empty:
            st.error("❌ Wind data missing 'electricity' column. Check API response.")
        else:
            wind_yield = wind_df["electricity"].sum()
            st.metric("Annual Wind Yield (kWh/kW @100m)", f"{wind_yield:.0f}")

            turbine_spacing_area = 367000  # m² per turbine based on Enercon E-101 3MW
            number_of_turbines = int(site_size // turbine_spacing_area)

            if number_of_turbines == 0:
                st.warning("⚠️ Site too small for a full wind turbine with proper spacing.")
            else:
                wind_capacity_kw = number_of_turbines * 3000  # Each turbine is 3MW = 3000kW
                wind_capex = wind_capacity_kw * 1700
                wind_generated = wind_yield * wind_capacity_kw
                wind_used = min(wind_generated, annual_consumption)
                wind_excess = max(0, wind_generated - annual_consumption)
                wind_savings = wind_used * 0.20 + wind_excess * export_price
                wind_payback = wind_capex / wind_savings if wind_savings > 0 else None

                st.write(f"**Estimated Turbines:** {number_of_turbines} x 3MW")
                st.write(f"**Total Wind Capacity:** {wind_capacity_kw:,} kW")
                st.write(f"**CapEx:** £{wind_capex:,.0f}")
                st.write(f"**Annual Savings:** £{wind_savings:,.0f}")
                st.write(f"**Estimated Payback:** {wind_payback:.1f} years" if wind_payback else "N/A")

    except Exception as e:
        st.error(f"❌ Error: {e}")
