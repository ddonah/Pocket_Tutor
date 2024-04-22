# Math Engine
# Taaon doing his best
import unittest
from sympy import Symbol
from sympy.parsing import parse_expr
from sympy.solvers import solve



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
    i=0
    
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

def postfix_to_infix(exp):
    s = [] 
    def isOperand(x):
        if len(x > 1) and x[0] == "-":
            return True
        elif x.isnumeric():
            return True
        else:
            return (x >= 'a' and x <= 'z') or (x >= 'A' and x <= 'Z')

    for i in exp:     
         
        # Push operands 
        if (isOperand(i)) :         
            s.insert(0, i) 
             
        # We assume that input is a 
        # valid postfix and expect 
        # an operator. 
        else:
         
            op1 = s[0] 
            s.pop(0) 
            op2 = s[0] 
            s.pop(0) 
            s.insert(0, "(" + op2 + i + op1 + ")") 
    return s[0]

class Equation():
    def __init__(self, inp):
        self.raw = inp
        if "=" in inp:
            self.problem = parse_expr(self.reorder(inp))
        else:
            self.problem = parse_expr(inp)
        self.target = None
        for ch in inp:
            if ch.isalpha():
                self.target = Symbol(ch)

    def __eq__(self, value:object) -> bool:
        return self.solve() == value.solve()
    def __ne__(self, value:object) -> bool:
        return self.solve() != value.solve()
    def __repr__(self) -> str:
        return self.problem
    def __str__(self) -> str:
        return str(self.problem)
    def __contains__(self, key)-> bool:
        return key in self.problem

    def solve(self):

        if self.target is None:
            return solve(self.problem, rational=None)[0]
        else:
            return solve(self.problem, self.target, rational=None)[0]

    def reorder(self, inp):
        # We will be working with self.problem, which in this case will be an equation in the form
        # nums = nums
        eq = inp.split("=")
        eq[0] = eq[0].split(" ")
        eq[1] = eq[1].split(" ")
        eq = ["("] + eq[0] + [")"] + [" - "] + ["("] + eq[1] + [")"]
        return " ".join(eq)

class Problem(Equation):
    # This class represents a line of a problem, you can solve for the answer
    def __init__(self, steps:list[str]|list[Equation]) -> None:
        if steps != []: # as in steps in the problem
            if type(list[0]) == str: # if strings or equations were passed
                steps = [Equation(step) for step in steps]


        self.steps = steps
        self.problem = steps[0] if steps != [] else None 
        # problem should be the first thing in the steps, everything is based off of that
    def __repr__(self) -> str:
        return [str(x) for x in (self.steps)]
    def __str__(self) -> str:
        return " |  ".join([str(x) for x in (self.steps)])
    
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
        missing = [x for x in operators if (counts[0][x] - counts[1][x])]
        
         
        '''print(counts)
        print(operator_locations)'''


    def kind_of_mistake(self, incorrect_steps:tuple):
        # In Development
        operators = ["^", "*", "/", "+", "-"]
        PEMDAS = "Pemdas Error"
        inequality = "did function incorrectly"
        



tests = ["2 * 3", "2 + 3 * 4", "a * b + 5", "a * b / c", "( a / ( b - c + d ) ) * ( e - a ) * c"]
answers = ["2 3 *","2 3 4 * +", "a b * 5 +", "a b * c /", "a b c - d + / e a - * c *"]

operators = {"^":5, "+":3, "-":3, "*": 4, "/":4}
association = {"^":'r', "+":'l', "-":'l', "*": 'l', "/":'l'}

a = Equation("4 * x = 2")
b = Equation("x = 2 / 4")
c = Problem([a, b])
print(c)


def main():
    usr_inp = input("Would you like to enter in an equation to solve, or steps from a problem? (e for equation, s for steps): ")
    if usr_inp == 'e':
        user_inp = input("Enter Equation with spaces between numbers: ")
        usr_eq = Equation(user_inp)
    elif usr_inp == 's':
        steps = []
        usr_inp = input("Please enter the current step or enter 'exit' to exit")
        while usr_inp != "exit":
            steps.append(usr_inp)
            usr_inp = input("Please enter the current step or enter 'exit' to exit")
        usr_problem = Problem(steps)

    else:
        print("I don't understand that input, please try again")



