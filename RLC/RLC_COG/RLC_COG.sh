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

set -e
set -x

#_______________________________________________________________________________
# echo running test.sh
cd "$owd"

# python ./test.py

python ./RLC_COG.py

# echo exiting test.sh
exit
#_______________________________________________________________________________
