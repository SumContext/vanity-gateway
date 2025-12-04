#!/usr/bin/env bash
#
# Permission is  hereby  granted,  free  of  charge,  to  any  person
# obtaining a copy of  this  software  and  associated  documentation
# files  (the  "Software"),  to  deal   in   the   Software   without
# restriction, including without limitation the rights to use,  copy,
# modify, merge, publish, distribute, sublicense, and/or sell  copies
# of the Software, and to permit persons  to  whom  the  Software  is
# furnished to do so.
#
# The above copyright notice and  this  permission  notice  shall  be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT  WARRANTY  OF  ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES  OF
# MERCHANTABILITY,   FITNESS   FOR   A   PARTICULAR    PURPOSE    AND
# NONINFRINGEMENT.  IN  NO  EVENT  SHALL  THE  AUTHORS  OR  COPYRIGHT
# OWNER(S) BE LIABLE FOR  ANY  CLAIM,  DAMAGES  OR  OTHER  LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING  FROM,
# OUT OF OR IN CONNECTION WITH THE  SOFTWARE  OR  THE  USE  OR  OTHER
# DEALINGS IN THE SOFTWARE.
#
######################################################################
utcupdate() { utc=$(date -u "+%Y.%m.%dT%H.%M.%SZ"); }
utcupdate  #UTC Time (filename safe)
owd="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #Path to THIS script.


# Define a function to run a script and log its output
# Usage: run_and_log <script> <logfile> [devshell]
run_and_log() { local script="$1" local logfile="$2" local devshell="$3"
    utcupdate
    echo "Running $script at $utc"

    if [[ -n "$devshell" ]]; then
        # Run inside nix-shell if devshell path is provided
        nix-shell "$devshell" --run "bash $script" 2>&1 | tee "$logfile"
#         nix-shell --option cores 3 "$devshell" --run "bash $script" 2>&1 | tee "$logfile"
    else
        # Otherwise run directly with bash
        bash "$script" 2>&1 | tee "$logfile"
    fi
    utcupdate
    echo "Completed $script at $utc"
}

combine_files() {
  # First argument is the output file
  output_file=$1
  shift   # Remove the first argument so only input files remain
  rm $output_file
  # Loop through all remaining arguments (the input files)
  for file in "$@"; do
    filename=$(basename "$file")
    # Print header with 10 # chars before and after
    {
      echo -e "#####\nFile: $filename\n######\n\n\`\`\`"
      # Escape triple backticks in file content
      sed 's/```/\\```/g' "$file"
      echo -e "\n\`\`\`"
    } >> "$output_file"
  done
}

######################################################################
echo $1

if [[ -n "$1" ]]; then
    owd="$1"
else
    :
fi

echo $owd


# Return to main dir
cd "$owd"

# Example call: run test.sh inside nix-shell, log to test_output.log
# run_and_log "$owd/test.sh" "$owd/test_output.log" "$owd/devShells.nix"
# run_and_log "$owd/RLC_COG.sh" "$owd/test_output.log" "$owd/devShells.nix"
run_and_log "$owd/dir_sum.sh" "$owd/test_output.log" "$owd/devShells.nix"

combine_files concat.md ./dir_sum2json.md ./dir_sum2json.py ./cog_cfg.json ./test_output.log
# combine_files concat.md ./devShells.nix ./RLC_COG.py ./RLC_COG.ui ./test_output.log

exit

######################################################################

# Test if your patch worked
cd ~/Papers-in-100-Lines-of-Code/Playing_Atari_with_Deep_Reinforcement_Learning
./concat_macro.sh

~/sync/RLC/concat_macro.sh ~/sync/RLC/RLC_COG
##########

# Version Control
cd ~/Papers-in-100-Lines-of-Code/Playing_Atari_with_Deep_Reinforcement_Learning
git gui &
