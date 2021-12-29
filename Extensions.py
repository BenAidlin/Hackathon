import random

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GeorgianFood:
    georgian_dishes = ['Churchkhela', 'Khachapuri', 'Kharcho', 'khinkali']
    get_random_georgian_dish = lambda : random.choice(GeorgianFood.georgian_dishes)

class MathProblems:
    def generate_problem():
        operators = ['+', '-', '*', '/']
        operator = random.choice(operators)
        operand1 = random.randint(1,9)
        operand2 = None
        if operator=='+':
            operand2 = random.randint(0, 9-operand1) # at least -> operator1, at most -> 9
            ans = operand1 + operand2
        if operator=='-':
            operand2 = random.randint(0, operand1) # at most -> operator1, at least -> 0
            ans = operand1 - operand2
        if operator=='*':
            operand2 = random.randint(0, int(9/operand1)) # at least -> 0, at most -> operator 1
            ans = operand1 * operand2
        if operator=='/': # most tricky
            operand2 = random.choice([i for i in range(1, operand1) if operand1%i==0]) # choose a number dividing operand2
            ans = operand1 / operand2
        
        return (str(operand1)+operator+str(operand2), str(ans)[0:1])