# print size(ders(CHAR("a"), "a"))  # Expected: 2
# Derivative of a sequence of characters
# x1 = der("a", SEQ(CHAR("a"), CHAR("b")))
# print "DER SEQUENCE TEST"
# print(isinstance(x1, SEQ))
# print x1.r1
# print x1.r2.c == "b"  

# Derivative of an alternation of characters
# x2 = der("a", ALT(CHAR("a"), CHAR("b")))
# print "DER ALTERNATION TEST"
# print(isinstance(x2, ALT))
# print x2.r1
# print x2.r2  

# Derivative of a star of a character
# x3 = der("a", STAR(CHAR("a")))
# print "DER STAR TEST"
# print(isinstance(x3, SEQ))
# print x3.r1
# print x3.r2
# print x3.r2.__repr__() ==  "STAR(CHAR(\"a\"))" 
# print RECD("cheese", SEQ(CHAR('c'), SEQ(CHAR('h'), SEQ(CHAR('e'), SEQ(CHAR('e'), SEQ(CHAR("s"), CHAR("e")))))))
# Derivative of a star of a character
# x3 = der("b", STAR(CHAR("a")))
# print "DER STAR FAIL TEST"
# print(isinstance(x3, SEQ))
# print x3.r1
# print x3.r2

# # Derivative of a range of characters
# x4 = der("a", RANGE("abc"))
# print(isinstance(x4, ONE))  # Expected: True

# # Derivative of a plus of a character
# x5 = der("a", PLUS(CHAR("a")))
# print(isinstance(x5, SEQ))  # Expected: True

# # Derivative of an optional character
# x6 = der("a", OPTIONAL(CHAR("a")))
# print(isinstance(x6, ONE))  # Expected: True

# # Derivative of a character not in the range
# x7 = der("d", RANGE("abc"))
# print(isinstance(x7, ZERO))  # Expected: True

# # Derivative of a sequence with nullable first part
# x8 = der("a", SEQ(OPTIONAL(CHAR("a")), CHAR("b")))
# print(isinstance(x8, ALT))  # Expected: True

# # Derivative of a recorded expression
# x9 = der("a", RECD("x", CHAR("a")))
# print(isinstance(x9, ONE))  # Expected: True

# # Derivative of a zero expression
# x10 = der("a", ZERO())
# print(isinstance(x10, ZERO))  # Expected: True

# # Derivative of a one expression
# x11 = der("a", ONE())
# print(isinstance(x11, ZERO))  # Expected: True

# # Derivative of a character that matches
# x12 = der("a", CHAR("a"))
# print(isinstance(x12, ONE))  # Expected: True

# # Derivative of a character that does not match
# x13 = der("b", CHAR("a"))
# print(isinstance(x13, ZERO))  # Expected: True

# # Derivative of a sequence with non-nullable first part
# x14 = der("a", SEQ(CHAR("a"), CHAR("b")))
# print(isinstance(x14, SEQ))  # Expected: True

# # Derivative of a sequence with nullable first part
# x15 = der("a", SEQ(OPTIONAL(CHAR("a")), CHAR("b")))
# print(isinstance(x15, ALT))  # Expected: True

# # Derivative of a star of a sequence
# x16 = der("a", STAR(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x16, SEQ))  # Expected: True

# # Derivative of a plus of a sequence
# x17 = der("a", PLUS(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x17, SEQ))  # Expected: True

# # Derivative of an optional sequence
# x18 = der("a", OPTIONAL(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x18, SEQ))  # Expected: True

# # Derivative of a recorded sequence
# x19 = der("a", RECD("x", SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x19, SEQ))  # Expected: True

# # Derivative of a sequence with a range
# x20 = der("a", SEQ(RANGE("abc"), CHAR("b")))
# print(isinstance(x20, SEQ))  # Expected: True

# print flatten(Sequ(Chr("a"), Chr("b")))  # Expected: "ab"
# print flatten(Stars([Chr("a"), Chr("b"), Chr("c")]))  # Expected: "abc"
# print flatten(Rng([Chr("a"), Chr("b"), Chr("c"), Empty()]))  # Expected: "abc"


# print env(Rec("x", Chr("a")))  # Expected: [("x", "a")]
# print env(Stars([Rec("x", Chr("a")), Rec("y", Chr("b"))]))  # Expected: [("x", "a"), ("y", "b")]
# print env(Rec("cheese", Sequ(Chr('c'), Sequ(Chr('h'), Sequ(Chr('e'), Sequ(Chr('e'), Sequ(Chr("s"), Chr("e"))))))))

# print mkeps(ALT(ONE(), CHAR("a")))  # Expected: Left(Empty)
# x = mkeps(SEQ(ONE(), NTIMES(0, CHAR("D"))))  # Expected: Sequ(Empty, Chr("a"))
# print x.v2

# regex = SEQ(CHAR("a"), CHAR("b"))
# der1 = der("a", regex)
# print der1
# der2 = der("b", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "b", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

# regex = SEQ(ALT(CHAR("a"), CHAR("b")), CHAR("c"))
# der1 = der("a", regex)
# print der1
# der2 = der("c", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "c", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

# regex = RECD("beans",STAR(CHAR("a")))
# der1 = der("a", regex)
# print der1
# der2 = der("a", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "a", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

# regex = NTIMES(CHAR("a"), 3)
# der1 = der("a", regex)
# print der1
# der2 = der("a", der1)
# print der2
# der3 = der("a", der2)
# print der3
# m = mkeps(der3)
# print m
# i = inj(der2, "a", m)
# print i
# n = inj(der1, "a", i)
# print n
# a = inj(regex, "a", n)
# print a
# print flatten(a)

# reg = ALT(ALT(ALT(CHAR("a"), ZERO()), CHAR("c")), CHAR("d"))
# print reg
# f, g = simp(reg)
# print f
# print g

# print lexing_simp(RECD("CD",STAR(CHAR("a"))), list("aaa"))
# print lexing_simp(RECD("AB",NTIMES(CHAR("a"), 3)), list("aaa"))
# print(lexing_simp(SEQ(CHAR("a"), CHAR("b")), "ab"))

# print regex_to_string(while_regex)  # Expected: "while"
# print regex_to_string(if_regex)  # Expected: "if"
# print regex_to_string(else_regex)  # Expected: "else"
# print regex_to_string(then_regex)  # Expected: "then"
# print regex_to_string(true_regex)  # Expected: "true"
# print regex_to_string(false_regex)  # Expected: "false"
# print regex_to_string(read_regex)  # Expected: "read"
# print regex_to_string(write_regex)  # Expected: "write"

# print lexing_simp(RECD("K", KEYWORD_REGEX), "while")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "if")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "then")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "else")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "true")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "false")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "read")
# print lexing_simp(RECD("K", KEYWORD_REGEX), "write")

# print lexing_simp(RECD("O", OPERATORS_REGEX), "+")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "-")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "*")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "/")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "%")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "==")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "!=")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "<")
# print lexing_simp(RECD("O", OPERATORS_REGEX), ">")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "<=")
# print lexing_simp(RECD("O", OPERATORS_REGEX), ">=")
# print lexing_simp(RECD("O", OPERATORS_REGEX), ":=")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "&&")
# print lexing_simp(RECD("O", OPERATORS_REGEX), "||")

# print lexing_simp(RECD("L", LETTERS_REGEX), "a")
# print lexing_simp(RECD("L", LETTERS_REGEX), "Z")

# print lexing_simp(RECD("S", SYMBOLS_REGEX), ".")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), "_")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), ">")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), "<")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), "=")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), ";")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), ",")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), "\\")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), ":")
# print lexing_simp(RECD("S", SYMBOLS_REGEX), "a")

# print lexing_simp(RECD("P", PARENTHESES_REGEX), "(")
# print lexing_simp(RECD("P", PARENTHESES_REGEX), ")")
# print lexing_simp(RECD("P", PARENTHESES_REGEX), "{")
# print lexing_simp(RECD("P", PARENTHESES_REGEX), "}")

# print lexing_simp(RECD("D", DIGITS_REGEX), "0")
# print lexing_simp(RECD("D", DIGITS_REGEX), "9")

# print lexing_simp(RECD("W", WHITESPACE_REGEX), "     ")
# print lexing_simp(RECD("W", WHITESPACE_REGEX), "\t")
# print lexing_simp(RECD("W", WHITESPACE_REGEX), "\n")

# print lexing_simp(RECD("I", IDENTIFIER_REGEX), "ab_s_")
# print lexing_simp(RECD("I", IDENTIFIER_REGEX), "Zdw90_")

# print lexing_simp(RECD("N", NUMBERS_REGEX), "0")
# print lexing_simp(RECD("N", NUMBERS_REGEX), "1")
# print lexing_simp(RECD("N", NUMBERS_REGEX), "903")

# print lexing_simp(RECD("S", STRING_REGEX), "\"a\"")
# print lexing_simp(RECD("S", STRING_REGEX), "\"Hello World\\n\"")

# print lexing_simp(RECD("C", COMMENT_REGEX), "// a my e re\n")
# print lexing_simp(RECD("C", COMMENT_REGEX), "// prints out prime numbers from\n")  # Should match correctly

# s = """
# while a == 0 {
#     a := a + 1
# };
# """
# c = """
# // prints out prime numbers from

# """
# print lexing_simp(LANGUAGE_REGEX, c)
# print lexing_simp(LANGUAGE_REGEX, "while a == 0")

# print T_KEYWORD("if") == T_KEYWORD("if")  # True
# print T_OP("+") == T_OP("+")  # True
# print T_STRING("hello") == T_STRING("hello")  # True
# print T_PAREN("(") == T_PAREN("(")  # True
# print T_ID("x") == T_ID("x")  # True
# print T_NUM(10) == T_NUM(10)  # True
# print T_SEMI() == T_SEMI()  # True

# print tokenise(c)