from spacyNER import SpaCyNER
import sys
import time

# please launch Stanford CoreNLP online server at first
start_time = time.time()
# First argument is save path, Second argument is sample number
SpaCyNER.run_training(sys.argv[1],int(sys.argv[2]))
print("--- %s seconds ---" % (time.time() - start_time))