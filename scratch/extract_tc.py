import json

with open(r"d:\03_Projects\LTW\Test2\scratch\edit_car_tc.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# The header is at row index 142 (approx)
# Columns: Module, Sub Module, ID, Kịch bản thử nghiệm, Quy trình, Điều kiện kiểm tra, Kết quả mong đợi, Test Data, ...

# Let's find the header row
header_row = -1
for i, row in enumerate(data):
    if "ID" in row and "Kịch bản thử nghiệm" in row:
        header_row = i
        headers = row
        break

if header_row == -1:
    print("Header not found")
    exit()

def get_col(row, col_name):
    try:
        idx = headers.index(col_name)
        return row[idx]
    except:
        return None

results = []
current_tc = {}

for row in data[header_row+1:]:
    tc_id = get_col(row, "ID")
    scenario = get_col(row, "Kịch bản thử nghiệm")
    steps = get_col(row, "Quy trình")
    expected = get_col(row, "Kết quả mong đợi")
    test_data = get_col(row, "Test Data")

    if tc_id:
        if current_tc:
            results.append(current_tc)
        current_tc = {
            "ID": tc_id,
            "Scenario": scenario,
            "Steps": [steps] if steps else [],
            "Expected": [expected] if expected else [],
            "TestData": test_data
        }
    else:
        if current_tc:
            if steps: current_tc["Steps"].append(steps)
            if expected: current_tc["Expected"].append(expected)
            if test_data and not current_tc["TestData"]: current_tc["TestData"] = test_data

if current_tc:
    results.append(current_tc)

# Write to markdown
with open(r"d:\03_Projects\LTW\Test2\scratch\edit_car_tc.md", "w", encoding="utf-8") as f:
    f.write("# Car Edit Test Cases\n\n")
    for tc in results:
        f.write(f"## {tc['ID']}: {tc['Scenario']}\n")
        f.write(f"**Steps:**\n- " + "\n- ".join(tc['Steps']) + "\n\n")
        f.write(f"**Expected:**\n- " + "\n- ".join(tc['Expected']) + "\n\n")
        f.write(f"**Test Data:** {tc['TestData']}\n\n")
        f.write("---\n\n")

print(f"Extracted {len(results)} test cases to scratch/edit_car_tc.md")
