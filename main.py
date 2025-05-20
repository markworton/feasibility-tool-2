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

include_battery = st.checkbox("Include Battery Storage?")
if include_battery:
    battery_capacity_kwh = st.number_input("Battery Capacity (kWh)", min_value=0)
    battery_round_trip_efficiency = st.number_input("Battery Round-Trip Efficiency (%)", min_value=0.0, max_value=100.0, value=90.0) / 100
    battery_cost_per_kwh = st.number_input("Battery Cost (£/kWh)", min_value=0.0, value=400.0)

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

            if include_battery:
                battery_eff = battery_round_trip_efficiency
                solar_used_direct = min(solar_generated, annual_consumption)
                solar_excess = max(0, solar_generated - annual_consumption)
                solar_stored = min(solar_excess, battery_capacity_kwh) * battery_eff
                solar_used = solar_used_direct + solar_stored
                solar_export = max(0, solar_excess - battery_capacity_kwh)
                solar_export_income = solar_export * export_price
            else:
                solar_used = min(solar_generated, annual_consumption)
                solar_export = max(0, solar_generated - annual_consumption)
                solar_export_income = solar_export * export_price

            solar_savings = solar_used * 0.20 + solar_export_income
            solar_payback = solar_cost / solar_savings if solar_savings > 0 else None

            st.write(f"**Estimated System Size:** {solar_kwp:.1f} kWp")
            st.write(f"**CapEx:** £{solar_cost:,.0f}")
            st.write(f"**Annual Savings (inc. export):** £{solar_savings:,.0f}")
            st.write(f"**Export Price:** £{export_price:.2f}/kWh")
            st.write(f"**Export Income from Excess:** £{solar_export_income:,.0f}")
            if include_battery:
                battery_cost = battery_capacity_kwh * battery_cost_per_kwh
                solar_cost += battery_cost
                st.write(f"**Battery Capacity:** {battery_capacity_kwh} kWh")
                st.write(f"**Battery Efficiency:** {battery_round_trip_efficiency*100:.0f}%")
                st.write(f"**Battery CapEx:** £{battery_cost:,.0f}")
            st.write(f"**Estimated Payback:** {solar_cost / solar_savings:.1f} years" if solar_savings else "N/A")

        st.divider()
        st.header("💨 Wind Feasibility")
        if "electricity" not in wind_df.columns or wind_df.empty:
            st.error("❌ Wind data missing 'electricity' column. Check API response.")
        else:
            wind_yield = wind_df["electricity"].sum()
            st.metric("Annual Wind Yield (kWh/kW @100m)", f"{wind_yield:.0f}")

            turbine_spacing_area = 367000
            number_of_turbines = int(site_size // turbine_spacing_area)

            if number_of_turbines == 0:
                st.warning("⚠️ Site too small for a full wind turbine with proper spacing.")
            else:
                wind_capacity_kw = number_of_turbines * 3000
                wind_capex = wind_capacity_kw * 1700
                wind_generated = wind_yield * wind_capacity_kw

                if include_battery:
                    wind_used_direct = min(wind_generated, annual_consumption)
                    wind_excess = max(0, wind_generated - annual_consumption)
                    wind_stored = min(wind_excess, battery_capacity_kwh) * battery_eff
                    wind_used = wind_used_direct + wind_stored
                    wind_export = max(0, wind_excess - battery_capacity_kwh)
                    wind_export_income = wind_export * export_price
                else:
                    wind_used = min(wind_generated, annual_consumption)
                    wind_export = max(0, wind_generated - annual_consumption)
                    wind_export_income = wind_export * export_price

                wind_savings = wind_used * 0.20 + wind_export_income
                if include_battery:
                    wind_capex += battery_capacity_kwh * battery_cost_per_kwh
                wind_payback = wind_capex / wind_savings if wind_savings > 0 else None

                st.write(f"**Estimated Turbines:** {number_of_turbines} x 3MW")
                st.write(f"**Total Wind Capacity:** {wind_capacity_kw:,} kW")
                st.write(f"**CapEx:** £{wind_capex:,.0f}")
                st.write(f"**Annual Savings (inc. export):** £{wind_savings:,.0f}")
                st.write(f"**Export Price:** £{export_price:.2f}/kWh")
                st.write(f"**Export Income from Excess:** £{wind_export_income:,.0f}")
                if include_battery:
                    st.write(f"**Battery Capacity:** {battery_capacity_kwh} kWh")
                    st.write(f"**Battery Efficiency:** {battery_round_trip_efficiency*100:.0f}%")
                st.write(f"**Estimated Payback:** {wind_payback:.1f} years" if wind_payback else "N/A")

    except Exception as e:
        st.error(f"❌ Error: {e}")
