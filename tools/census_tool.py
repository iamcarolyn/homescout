import httpx
from crewai.tools import tool


@tool("census_tool")
def census_tool(zip_code: str) -> str:
    """Fetch Census Bureau ACS5 demographic data for a zip code. Returns median income,
    median home value, population, owner/renter counts."""
    variables = {
        "B19013_001E": "median_household_income",
        "B25077_001E": "median_home_value",
        "B01003_001E": "total_population",
        "B25003_002E": "owner_occupied_units",
        "B25003_003E": "renter_occupied_units",
    }
    var_str = ",".join(variables.keys())
    url = (
        f"https://api.census.gov/data/2022/acs/acs5"
        f"?get={var_str}&for=zip%20code%20tabulation%20area:{zip_code}"
    )
    try:
        resp = httpx.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2:
            return "Census data not available for this zip code."
        headers = data[0]
        values = data[1]
        row = dict(zip(headers, values))
        result = {}
        for var_code, label in variables.items():
            val = row.get(var_code, None)
            if val is None or val in ("-666666666", -666666666, "-999999999"):
                result[label] = "Data not available"
            else:
                try:
                    result[label] = int(val)
                except (ValueError, TypeError):
                    result[label] = "Data not available"
        lines = [f"Census ACS5 data for ZIP {zip_code}:"]
        for k, v in result.items():
            label = k.replace("_", " ").title()
            if isinstance(v, int):
                if "income" in k or "value" in k:
                    lines.append(f"  {label}: ${v:,}")
                else:
                    lines.append(f"  {label}: {v:,}")
            else:
                lines.append(f"  {label}: {v}")
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        return f"Census API error {e.response.status_code}: {str(e)}"
    except Exception as e:
        return f"Census tool error: {str(e)}"
