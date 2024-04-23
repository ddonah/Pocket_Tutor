# Math Engine
# Taaon doing his best
import unittest
from sympy import Symbol
from sympy import N as solve_nums
from sympy.parsing import parse_expr
from sympy.solvers import solve as solve_for_target


# Defunct, do not use.
"""class TestFns(unittest.TestCase):
    def test_infix_to_postfix(self):
        tests = ["2 + 3 * 4", "a*b+5", "(1+2)*7", "a * b / c", "( a / ( b - c + d ) ) * ( e - a ) * c"]
        answers = ["2 3 4 * +", "a b * 5 +", "a b * c /", "a b c - d + / e a - * c *"]
        for i in range(len(tests)):
            res = infix_to_postfix(tests[i])
            self.assertEqual(answers[i], res)"""

def pemdas(char):
    # Helper function for changing infix to postfix, returns int representing hierarhy
    if char == '^':
        return 3
    elif char == '/' or char == '*':
        return 2
    elif char == '+' or char == '-':
        return 1
    else:
        return -1

def associativity(c):
    # Another helper function for the infix to postfix fn
    if c == '^':
        return 'R'
    return 'L'

def infix_to_postfix(s):
    # does what function says through utilizing a stack and helper functions.
    # returns string
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
    # same thing as infix, except turns to infix
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
    '''
    This function represents a line of an equation, it allows manipulation of the equations through sympy
    and also can use equivalencies to allow future usage of systems of equations
    '''
    def __init__(self, inp):
        # for checking for mistakes
        self.raw = inp
        # an equals sign must always have a target which equates to a variable to solve for
        if "=" in inp:
            self.problem = parse_expr(self.reorder(inp), evaluate=False)
        else:
            self.problem = parse_expr(inp, evaluate=False)
        self.target = None
        # searches for first non-numeric character in equation to set as target
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
        '''
        Sympy defines their solve function as only solving for variables
        simple algebra is defined as simplification, thus the different functions
        '''
        if self.target is None:
            return solve_nums(self.problem) # solve_nums() is the sympy.N() function aliased
        else:
            return solve_for_target(self.problem, self.target, rational=None)[0] # solve_for_target is sympy.solvers.solve() function aliased

    def reorder(self, inp:str):
        """
        This equation will return a string representing an equation equaling zero.
        It's very basic but as an example x + 4 = 7 would return (x + 4) - (7). 
        This is so sympy can then process the function
        inp is the equation to be reordered.
        """
        eq = inp.split("=")
        eq[0] = eq[0].split(" ")
        eq[1] = eq[1].split(" ")
        eq = ["("] + eq[0] + [")"] + [" - "] + ["("] + eq[1] + [")"]
        return " ".join(eq)

class Problem(Equation):
    """
    This represents the steps of a problem as entered into a file to be read.
    It is essentially a list of Equation instances but adds some additional capability.
    """
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
    
    def check_for_mistakes(self) -> str:
        '''
        Assuming there are no mistakes, this program will return None, otherwise it will return
        the first operator in found to be different between the two steps.
        '''
        mistake = None 
        for i in range(1, len(self.steps)): 
            
            if self.steps[i] != self.steps[i-1]:# Comparing step with the step before it
                mistake = (self.steps[i-1], self.steps[i])
                break
        if not mistake: # Checking for all lines being equivalent
            return "No mistakes found! Good Work!"
        failed_step = i +1
        
        operators = ["^", "*", "/", "+", "-"]
        counts = {0:{"^":0, "*":0, "/":0, "+":0, "-":0}, 1:{"^":0, "*":0, "/":0, "+":0, "-":0}}
        #operator_locations = {'prev':{"^":[], "*":[], "/":[], "+":[], "-":[]}, 'curr':{"^":[], "*":[], "/":[], "+":[], "-":[]}}
        prev_step = mistake[0].raw
        curr_step = mistake[1].raw

        # for j in range(length(equation class))
        for i in range(len(prev_step)):
             # Selecting first problem from mistake container
            if prev_step[i] in operators:
                counts[0][prev_step[i]] += 1 # Keeping track of operator counts
                #operator_locations[0][eq[j]].insert(0, (j, eq[j])) # insert tuple with format (index position, operator)
        for i in range(len(curr_step)):
            if curr_step[i] in operators:
                counts[1][curr_step[i]] += 1
        # Find the missing operator
        missing = [x for x in operators if (counts[0][x] - counts[1][x])]
        return self.define_mistake(missing[0], failed_step)
    
    @staticmethod
    def define_mistake(inp, step_num) -> str:
        error = ["You've made a ", None, " error on step " , str(step_num)]
        if inp == '*':
            error[1] = "multiplication"
        elif inp == '/':
            error[1] = "division"
        elif inp == '+':
            error[1] = "addition"
        elif inp == '-':
            error[1] = "subtraction"
        elif inp == '^':
            error[1] = "exponation"
        else:
            return "We aren't sure what error you made, but it was on step " + str(step_num)
        return "".join(error)





def read_file(fname:str) -> Problem:
    file = open(fname, 'r')
    return Problem([Equation(x.rstrip('\n')) for x in file.readlines()])

def main():
    fname = input("enter filename please")
    problem = read_file(fname)
    mistakes = problem.check_for_mistakes()
    file = open("mistakes.txt", 'w')
    file.write(mistakes)
    file.close()



