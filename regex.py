# regex engine in Python
# xiayun.sun@gmail.com
# 06-JUL-2013
# currently supporting: alteration(|), concatenation, star(*) operator
# TODO: 
#     more rigorous bnf grammar for regex                 DONE
#     add . 
#     better unit tests                                   DONE
#     backreferences? NO
#     convert to DFA
#     draw NFA in debug mode using Graphviz


from parse import Lexer, Parser, Token, State, NFA
import pdb, re, time

state_i = 0

def create_state():
    global state_i # TODO: better than global variable?
    state_i += 1
    return State('s' + str(state_i))

def print_tokens(tokens):
    for t in tokens:
        print(t)

def compile(p, debug = False):
    lexer = Lexer(p)
    parser = Parser(lexer)
    tokens = parser.parse()
    if debug:
        print_tokens(tokens) 

    nfa_stack = []
    for t in tokens:
        
        if t.name == 'CHAR':  
            s0 = create_state()
            s1 = create_state()
            s0.transitions[t.value] = s1
            nfa = NFA(s0, s1)
            nfa_stack.append(nfa)
        
        elif t.name == 'CONCAT':
            n2 = nfa_stack.pop()
            n1 = nfa_stack.pop()
            n1.end.is_end = False
            n1.end.epsilon.append(n2.start)
            nfa = NFA(n1.start, n2.end)
            nfa_stack.append(nfa)
        
        elif t.name == 'ALT':
            n2 = nfa_stack.pop()
            n1 = nfa_stack.pop()
            s0 = create_state()
            s0.epsilon = [n1.start, n2.start]
            s3 = create_state()
            n1.end.epsilon.append(s3)
            n2.end.epsilon.append(s3)
            n1.end.is_end = False
            n2.end.is_end = False
            nfa = NFA(s0, s3)
            nfa_stack.append(nfa)
        
        elif t.name == 'STAR':
            n1 = nfa_stack.pop()
            s0 = create_state()
            s1 = create_state()
            s0.epsilon = [n1.start, s1]
            n1.end.epsilon.extend([s1, n1.start])
            n1.end.is_end = False
            nfa = NFA(s0, s1)
            nfa_stack.append(nfa)

        elif t.name == 'PLUS':
            n1 = nfa_stack.pop()
            s0 = create_state()
            s1 = create_state()
            n1.end.is_end = False
            s0.epsilon = [n1.start]
            n1.end.epsilon.extend([s1, n1.start])
            nfa = NFA(s0, s1)
            nfa_stack.append(nfa)
        
        elif t.name == 'QMARK':
            n1 = nfa_stack.pop()
            n1.start.epsilon.append(n1.end)
            nfa_stack.append(n1)
    
    assert len(nfa_stack) == 1
    return nfa_stack.pop() 

def main(debug = False):
    global status_i
    status_i = 0
    
    nfa = compile('(Ab|cD)*', debug)
    if debug:
        nfa.pretty_print()
    print(nfa.match('Abc'))

def test_pathological(n):
    p = 'a?' * n + 'a' * n
    nfa_python = re.compile(p)
    nfa_me = compile(p)
    string = 'a' * n
    # test python
    t0 = time.time()
    m = nfa_python.match(string)
    print("Python:", time.time() - t0)
    print("result:", m)
    # test mine
    t0 = time.time()
    m = nfa_me.match(string)
    print("Thompson's Algo:", time.time() - t0)
    print("result:", m)

if __name__ == '__main__':
    main(debug = True)
