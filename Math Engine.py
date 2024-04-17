# Math Engine
import unittest, regex


class TestFns(unittest.TestCase):
    def test_infix_to_postfix(self):
        tests = ["2 + 3 * 4", "a*b+5", "(1+2)*7", "a * b / c", "( a / ( b - c + d ) ) * ( e - a ) * c"]
        answers = ["2 3 4 * +", "a b * 5 +", "a b * c /", "a b c - d + / e a - * c *"]
        for i in range(len(tests)):
            res = infix_to_postfix(tests[i])
            self.assertEqual(answers[i], res)

def pemdas(char):
    if char == '^':
        return 3
    elif char == '/' or char == '*':
        return 2
    elif char == '+' or char == '-':
        return 1
    else:
        return -1

def postfix_to_infix(s):
    pass

def associativity(c):
    if c == '^':
        return 'R'
    return 'L'

def infix_to_postfix(s):
    result = []
    stack = []
    i =0
    while i < len(s):
        c = s[i]
        if c == " ":
            i += 1
            continue
        # If the scanned character is an operand, add it to the output string.
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9'):
            num = ""
            while i < len(s) and s[i] != " ":
                num += s[i]
                i+=1
            result.append(num)
        # If the scanned character is an ‘(‘, push it to the stack.
        elif c == '(':
            stack.append(c)
        # If the scanned character is an ‘)’, pop and add to the output string from the stack
        # until an ‘(‘ is encountered.
        elif c == ')':
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            stack.pop()  # Pop '('
        # If an operator is scanned
        else:
            while stack and (pemdas(s[i]) < pemdas(stack[-1]) or
                             (pemdas(s[i]) == pemdas(stack[-1]) and associativity(s[i]) == 'L')):
                result.append(stack.pop())
            stack.append(c)
        i += 1
 
    # Pop all the remaining elements from the stack
    while stack:
        result.append(stack.pop())
 
    return ' '.join(result)

def postfix_to_infix(s):
    pass

class Equation():
    def __init__(self, inp, inFix=True):
        if inFix:
            self.problem = infix_to_postfix(inp)
        else:
            self.problem = inp
        self.answer = None
    def __eq__(self, value:object) -> bool:
        return self.solve() == value.solve()
    def __ne__(self, value:object):
        return self.solve() != value.solve()
    def __repr__(self):
        return self.problem

    def solve(self, target=None):
        operations = {"^": lambda x, y: x**y, "*": lambda x, y:x*y, "/": lambda x, y: x / y, "+": lambda x, y: x+y, "-": lambda x, y: x-y}

        eq = self.problem.split(" ")
        operators = ["^", "*", "/", "+", "-"]
        cursor = 0
        if len(eq) == 1:
            return str(float("".join(eq)))
        while any([op for op in operators if(op in eq)]):
            if eq[cursor] not in operators:
                cursor += 1
                continue
            fn = operations[eq[cursor]]
            location = cursor
            insert_index = location-2
            operand1, operand2 = eq[location-2], eq[location-1]
            eq.pop(location)
            eq.pop(location-1)
            eq.pop(location-2)
            cursor = location-2
            eq.insert(insert_index, str(fn(float(operand1), float(operand2))))
        return "".join(eq)

    def reorder(self, target):
        pass


class Problem(Equation):
    # This class represents a line of a problem, you can solve for the answer
    def __init__(self, steps:list[str]|list[Equation]) -> None:
        if steps != []: # as in steps in the problem
            if type(list[0]) == str: # if strings or equations were passed
                steps = [Equation(step) for step in steps]


        self.steps = steps
        self.problem = steps[0] if steps != [] else None 
        # problem should be the first thing in the steps, everything is based off of that
    
    def check_for_mistakes(self):
        #Assuming there are no mistakes, this program will return None, otherwise it will return a tuple
        # of the operator and the index of the operator in the step
        mistake = None 
        for i in range(1, len(self.steps)): 
            if self.steps[i] != self.steps[i-1]:# Comparing step with the step before it
                mistake = (self.steps[i-1], self.steps[i])
                break
        if not mistake: # Checking for all lines being equivalent
            return mistake
        
        operators = ["^", "*", "/", "+", "-"]
        counts = {0:{"^":0, "*":0, "/":0, "+":0, "-":0}, 1:{"^":0, "*":0, "/":0, "+":0, "-":0}}
        operator_locations = {0:{"^":[], "*":[], "/":[], "+":[], "-":[]}, 1:{"^":[], "*":[], "/":[], "+":[], "-":[]}}

        # for j in range(length(equation))
        # mistake[0].problem = some equation
        for j in range(len(mistake[0].problem)):
            eq = mistake[0].problem # Selecting first problem from mistake container
            if eq[j] in operators:
                counts[0][eq[j]] += 1 # Keeping track of operator counts
                operator_locations[0][eq[j]].insert(0, (j, eq[j])) # insert tuple with format (index position, operator)

        # See last loop
        for j in range(len(mistake[1].problem)):
            if mistake[1].problem[j] in operators:
                counts[1][mistake[1].problem[j]] += 1
                operator_locations[1][mistake[1].problem[j]].insert(0, (j, mistake[1].problem[j]))
        
        # Find the missing operator
         
        print(counts)
        print(operator_locations)


    def kind_of_mistake(self, incorrect_steps:tuple):
        # In Development
        operators = ["^", "*", "/", "+", "-"]
        PEMDAS = "Pemdas Error"
        inequality = "did function incorrectly"
        



tests = ["2 * 3", "2 + 3 * 4", "a * b + 5", "a * b / c", "( a / ( b - c + d ) ) * ( e - a ) * c"]
answers = ["2 3 *","2 3 4 * +", "a b * 5 +", "a b * c /", "a b c - d + / e a - * c *"]

operators = {"^":5, "3":4, "-":3, "*": 4, "/":4}
association = {"^":'r', "3":'l', "-":'l', "*": 'l', "/":'l'}

a = Equation("5 * 2 + 3 * 5")
b = Equation("10 + 15")
c = Equation("30")
d = Problem([a, b, c])
print(d.check_for_mistakes())
