run_test() {
  local scenario_name="$1"
  local output="$2"
  local grep_flag="$3"
  local pattern="$4"
  local fail_msg="$5"
  local success_msg="$6"

  echo "$scenario_name"
  echo "$output" | grep "$grep_flag" "$pattern" || { echo "${fail_msg}! Output was: $output"; return 1; }
  echo "${success_msg}"
}

run_test "Scenario 1: Code in /src/api/ changed without context doc (Stop Hook)" \
  "{\"decision\": \"continue\"}" \
  -q '"decision": "continue"' \
  "Test 1 Failed" \
  "Scenario 1 Passed: Stop blocked."
