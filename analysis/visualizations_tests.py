import matplotlib.pyplot as plt

# Data for the bar chart
modules = ['test_chatbot.py', 'test_db_helper.py', 'test_generic_helper.py', 'test_integration.py', 'test_main.py']
tests_passed = [1, 6, 3, 1, 5]

# Create bar chart
plt.figure(figsize=(10, 6))
plt.bar(modules, tests_passed, color='skyblue')
plt.xlabel('Test Modules')
plt.ylabel('Number of Tests Passed')
plt.title('Number of Tests Passed by Module')
plt.xticks(rotation=45)
plt.tight_layout()


plt.show()


import matplotlib.pyplot as plt

# Data for the execution time graph
execution_time = 2.34


plt.figure(figsize=(6, 4))
plt.bar('Total Execution Time', execution_time, color='lightgreen')
plt.ylabel('Seconds')
plt.title('Total Execution Time for All Tests')


plt.show()
