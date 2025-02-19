// CW3
//======
//
// The main idea is to extend the parser form the lectures 
// (which processes strings) to a parser that processes
// tokens. For this you need to use the lexer from CW2 and
// possibly adjust the lexing regular expressions accordingly.


// IMPORTANT:
//
// you need to include the lexer from CW2, which defines
// Tokens and tokenise
// 
// one way to do it is via the import statements
//
// import $file.^.cw2.cw02
// import cw02._
//
// or copy the code into this directory / file


// Rexps
abstract class Rexp
case object ZERO extends Rexp
case object ONE extends Rexp
case class CHAR(c: Char) extends Rexp
case class ALT(r1: Rexp, r2: Rexp) extends Rexp 
case class SEQ(r1: Rexp, r2: Rexp) extends Rexp 
case class STAR(r: Rexp) extends Rexp 

// new regular expressions
case class RANGE(s: Set[Char]) extends Rexp
case class PLUS(r: Rexp) extends Rexp
case class OPTIONAL(r: Rexp) extends Rexp
case class NTIMES(r: Rexp, n: Int) extends Rexp 
case class RECD(x: String, r: Rexp) extends Rexp

// values
abstract class Val
case object Empty extends Val
case class Chr(c: Char) extends Val
case class Sequ(v1: Val, v2: Val) extends Val
case class Left(v: Val) extends Val
case class Right(v: Val) extends Val
case class Stars(vs: List[Val]) extends Val
case class Rec(x: String, v: Val) extends Val
case class Rng(cs : Set[Val]) extends Val
case class Pls(vs : List[Val]) extends Val
case class Opt(v : Val) extends Val
case class Ntms(vs : List[Val]) extends Val

// some convenience for typing in regular expressions
import scala.language.implicitConversions

def charlist2rexp(s : List[Char]): Rexp = s match {
  case Nil => ONE
  case c::Nil => CHAR(c)
  case c::s => SEQ(CHAR(c), charlist2rexp(s))
}

given Conversion[String, Rexp] = (s => charlist2rexp(s.toList))

extension (s: String) {
  def & (r: Rexp) = RECD(s, r)
  def | (r: Rexp) = ALT(s, r)
  def | (r: String) = ALT(s, r)
  def % = STAR(s)
  def ~ (r: Rexp) = SEQ(s, r)
  def ~ (r: String) = SEQ(s, r)
}

extension (r: Rexp) {
  def ~ (s: Rexp) = SEQ(r, s)
  def % = STAR(r)
  def | (s: Rexp) = ALT(r, s)
}

// nullable 
def nullable(r: Rexp) : Boolean = r match {
  case ZERO => false
  case ONE => true
  case CHAR(_) => false
  case ALT(r1, r2) => nullable(r1) || nullable(r2)
  case SEQ(r1, r2) => nullable(r1) && nullable(r2)
  case STAR(_) => true
  case RANGE(_) => false
  case PLUS(r) => nullable(r)
  case OPTIONAL(_) => true
  case NTIMES(r, i) => if (i == 0) true else nullable(r)
  case RECD(_, r) => nullable(r)
}

// der 
def der(c: Char, r: Rexp) : Rexp = r match {
  case ZERO => ZERO
  case ONE => ZERO
  case CHAR(d) => if (c == d) ONE else ZERO
  case ALT(r1, r2) => ALT(der(c, r1), der(c, r2))
  case SEQ(r1, r2) => 
    if (nullable(r1)) ALT(SEQ(der(c, r1), r2), der(c, r2))
    else SEQ(der(c, r1), r2)
  case STAR(r) => SEQ(der(c, r), STAR(r))
  case RANGE(cs) => if (cs.contains(c)) ONE else ZERO
  case PLUS(r) => SEQ(der(c, r), STAR(r))
  case OPTIONAL(r) => der(c, r)
  case NTIMES(r, i) => 
    if (i == 0) ZERO else SEQ(der(c, r), NTIMES(r, i - 1))
  case RECD(_, r) => der(c, r)
}

// flatten
def flatten(v: Val) : String = v match {
  case Empty => ""
  case Chr(c) => c.toString
  case Left(v) => flatten(v)
  case Right(v) => flatten(v)
  case Sequ(v1, v2) => flatten(v1) + flatten(v2)
  case Stars(vs) => vs.map(flatten).mkString
  case Rng(cs) => cs.map {
    case Chr(c) => c.toString
  }.mkString
  case Pls(vs) => vs.map(flatten).mkString
  case Opt(v) => flatten(v)
  case Ntms(vs) => vs.map(flatten).mkString
  case Rec(_, v) => flatten(v)
}

// env 
def env(v: Val) : List[(String, String)] = v match {
  case Empty => Nil
  case Chr(c) => Nil
  case Left(v) => env(v)
  case Right(v) => env(v)
  case Sequ(v1, v2) => env(v1) ::: env(v2)
  case Stars(vs) => vs.flatMap(env)
  case Rng(cs) => Nil
  case Pls(vs) => vs.flatMap(env)
  case Opt(v) => env(v)
  case Ntms(vs) => vs.flatMap(env)
  case Rec(x, v) => (x, flatten(v))::env(v)
}

// mkeps 
def mkeps(r: Rexp) : Val = r match {
  case ONE => Empty
  case ALT(r1, r2) => 
    if (nullable(r1)) Left(mkeps(r1)) else Right(mkeps(r2))
  case SEQ(r1, r2) => Sequ(mkeps(r1), mkeps(r2))
  case STAR(r) => Stars(Nil)
  case PLUS(r) => Pls(List(mkeps(r)))
  case OPTIONAL(r) => Opt(Empty)
  case NTIMES(r, n) => 
    if (n == 0) Ntms(Nil) 
    else Ntms(List(mkeps(r)))
  case RECD(x, r) => Rec(x, mkeps(r)) 
}

// inj 
def inj(r: Rexp, c: Char, v: Val): Val = (r, v) match {
  case (STAR(r), Sequ(v1, Stars(vs))) => Stars(inj(r, c, v1) :: vs)
  case (SEQ(r1, r2), Sequ(v1, v2)) => Sequ(inj(r1, c, v1), v2)
  case (SEQ(r1, r2), Left(Sequ(v1, v2))) => Sequ(inj(r1, c, v1), v2)
  case (SEQ(r1, r2), Right(v2)) => Sequ(mkeps(r1), inj(r2, c, v2))
  case (ALT(r1, r2), Left(v1)) => Left(inj(r1, c, v1))
  case (ALT(r1, r2), Right(v2)) => Right(inj(r2, c, v2))
  case (CHAR(d), Empty) => Chr(c)
  case (RANGE(cs), Empty) => Chr(c)
  case (PLUS(r), Sequ(v1, Stars(vs))) => Pls(inj(r, c, v1) :: vs)
  case (OPTIONAL(r), v) => Opt(inj(r, c, v))
  case (NTIMES(r, n), Sequ(v1, Ntms(vs))) => Ntms(inj(r, c, v1) :: vs)
  case (RECD(x, r), v) => Rec(x, inj(r, c, v))
}


// the simplification and rectification part

// rectification functions
def F_ID(v: Val): Val = v
def F_RIGHT(f: Val => Val) = (v:Val) => Right(f(v))
def F_LEFT(f: Val => Val) = (v:Val) => Left(f(v))
def F_ALT(f1: Val => Val, f2: Val => Val) = (v:Val) => v match {
  case Right(v) => Right(f2(v))
  case Left(v) => Left(f1(v))
}
def F_SEQ(f1: Val => Val, f2: Val => Val) = (v:Val) => v match {
  case Sequ(v1, v2) => Sequ(f1(v1), f2(v2))
}
def F_SEQ_Empty1(f1: Val => Val, f2: Val => Val) = 
  (v:Val) => Sequ(f1(Empty), f2(v))
def F_SEQ_Empty2(f1: Val => Val, f2: Val => Val) = 
  (v:Val) => Sequ(f1(v), f2(Empty))
def F_RECD(f: Val => Val) = (v:Val) => v match {
  case Rec(x, v) => Rec(x, f(v))
}
def F_ERROR(v: Val): Val = throw new Exception("error")

// simp
def simp(r: Rexp): (Rexp, Val => Val) = r match {
  case ALT(r1, r2) => {
    val (r1s, f1s) = simp(r1)
    val (r2s, f2s) = simp(r2)
    (r1s, r2s) match {
      case (ZERO, _) => (r2s, F_RIGHT(f2s))
      case (_, ZERO) => (r1s, F_LEFT(f1s))
      case _ => if (r1s == r2s) (r1s, F_LEFT(f1s))
                else (ALT (r1s, r2s), F_ALT(f1s, f2s)) 
    }
  }
  case SEQ(r1, r2) => {
    val (r1s, f1s) = simp(r1)
    val (r2s, f2s) = simp(r2)
    (r1s, r2s) match {
      case (ZERO, _) => (ZERO, F_ERROR)
      case (_, ZERO) => (ZERO, F_ERROR)
      case (ONE, _) => (r2s, F_SEQ_Empty1(f1s, f2s))
      case (_, ONE) => (r1s, F_SEQ_Empty2(f1s, f2s))
      case _ => (SEQ(r1s,r2s), F_SEQ(f1s, f2s))
    }
  }
  case r => (r, F_ID) // this part handles all new regular expressions
}

// lexing generating a value
def lex_simp(r: Rexp, s: List[Char]) : Val = s match {
  case Nil => if (nullable(r)) mkeps(r) else 
    { throw new Exception("lexing error") } 
  case c::cs => {
    val (r_simp, f_simp) = simp(der(c, r))
    inj(r, c, f_simp(lex_simp(r_simp, cs)))
  }
}

// lexing extracting a list of String-String pairs 
def lexing_simp(r: Rexp, s: String) : List[(String, String)] = env(lex_simp(r, s.toList))


// Language specific code for the While Language 

val KEYWORD: Rexp = "while" | "if" | "then" | "else" | "do" | "for" | "to" | "true" | "false" | "read" | "write" | "skip"
val OP: Rexp = "+" | "-" | "*" | "%" | "/" | "==" | "!=" | ">" | "<" | "<=" | ">=" | ":=" | "&&" | "||"
val LET: Rexp = RANGE(('A' to 'Z').toSet ++ ('a' to 'z').toSet)
val SYM: Rexp = LET | "." | "_" | ">" | "<" | "=" | ";" | "," | "\\" | ":"
val PARENS: Rexp = "(" | "{" | ")" | "}"
val DIGIT: Rexp = RANGE(('0' to '9').toSet)
val SEMI: Rexp = ";"
val WHITESPACE: Rexp = PLUS(" ") | "\n" | "\t" | "\r"
val ID: Rexp = LET ~ (LET | DIGIT | "_").%
val NUMBERS: Rexp = "0" | (RANGE(('1' to '9').toSet) ~ DIGIT.%)
val STRING: Rexp = "\"" ~ (SYM | DIGIT | PARENS | WHITESPACE | "\\n").% ~ "\""
val EOL: Rexp = "\n" | "\r\n"
val COMMENT: Rexp = "//" ~ (SYM | " " | PARENS | DIGIT).% ~ EOL

val WHILE_REGS = (("k" & KEYWORD) | 
                  ("o" & OP) | 
                  ("str" & STRING) |
                  ("p" & PARENS) |
                  ("s" & SEMI) |
                  ("w" & WHITESPACE) | 
                  ("i" & ID) | 
                  ("n" & NUMBERS) |
		              ("c" & COMMENT)).%

// Token
abstract class Token extends Serializable 
case class T_KEYWORD(s: String) extends Token
case class T_OP(s: String) extends Token
case class T_STRING(s: String) extends Token
case class T_PAREN(s: String) extends Token
case object T_SEMI extends Token
case class T_ID(s: String) extends Token
case class T_NUM(n: Int) extends Token

val token : PartialFunction[(String, String), Token] = {
  case ("k", s) => T_KEYWORD(s)
  case ("o", s) => T_OP(s)
  case ("str", s) => T_STRING(s)
  case ("p", s) => T_PAREN(s)
  case ("s", _) => T_SEMI
  case ("i", s) => T_ID(s)
  case ("n", s) => T_NUM(s.toInt)
}

// Tokenise
def tokenise(s: String) : List[Token] = lexing_simp(WHILE_REGS, s).collect(token)


// parser combinators

type IsSeq[I] = I => Seq[_]

abstract class Parser[I, T](using is: IsSeq[I])  {
  def parse(in: I): Set[(T, I)]  

  def parse_all(in: I) : Set[T] =
    for ((hd, tl) <- parse(in); 
        if is(tl).isEmpty) yield hd
}

// parser combinators

// alternative parser
class AltParser[I : IsSeq, T](p: => Parser[I, T], 
                              q: => Parser[I, T]) extends Parser[I, T] {
  def parse(in: I) = p.parse(in) ++ q.parse(in)   
}

// sequence parser
class SeqParser[I: IsSeq, T, S](p: => Parser[I, T], 
                                q: => Parser[I, S]) extends Parser[I, (T, S)] {
  def parse(in: I) = 
    for ((hd1, tl1) <- p.parse(in); 
         (hd2, tl2) <- q.parse(tl1)) yield ((hd1, hd2), tl2)
}

// map parser
class MapParser[I : IsSeq, T, S](p: => Parser[I, T], 
                         f: T => S) extends Parser[I, S] {
  def parse(in: I) = for ((hd, tl) <- p.parse(in)) yield (f(hd), tl)
}


// some convenient syntax for parser combinators
extension [I: IsSeq, T](p: Parser[I, T]) {
  def ||(q : => Parser[I, T]) = new AltParser[I, T](p, q)
  def ~[S] (q : => Parser[I, S]) = new SeqParser[I, T, S](p, q)
  def map[S](f: => T => S) = new MapParser[I, T, S](p, f)
}

// atomic parser for (particular) tokens
case class TokenParser(t: Token) extends Parser[List[Token], Token] {
  def parse(in: List[Token]) = in match {
    case hd :: tl if hd == t => Set((hd, tl))
    case _ => Set()
  }
}

// atomic parser for identifiers (variable names)
case object IdParser extends Parser[List[Token], String] {
  def parse(in: List[Token]) = in match {
    case T_ID(s) :: tl => Set((s, tl))
    case _ => Set()
  }
}

// atomic parser for numbers (transformed into Ints)
case object NumParser extends Parser[List[Token], Int] {
  def parse(in: List[Token]) = in match {
    case T_NUM(i) :: tl => Set((i.toInt, tl))
    case _ => Set()
  }
}

// atomic parser for strings
case object StringParser extends Parser[List[Token], String] {
  def parse(in: List[Token]) = in match {
    case T_STRING(s) :: tl => Set((s, tl))
    case _ => Set()
  }
}

// parsers for arithmetic expressions
val plusParser = TokenParser(T_OP("+"))
val minusParser = TokenParser(T_OP("-"))
val mulParser = TokenParser(T_OP("*"))
val divParser = TokenParser(T_OP("/"))
val modParser = TokenParser(T_OP("%"))
val lparenParser = TokenParser(T_PAREN("("))
val rparenParser = TokenParser(T_PAREN(")"))

// parsers for boolean expressions
val eqParser = TokenParser(T_OP("=="))
val neqParser = TokenParser(T_OP("!="))
val ltParser = TokenParser(T_OP("<"))
val gtParser = TokenParser(T_OP(">"))
val leParser = TokenParser(T_OP("<="))
val geParser = TokenParser(T_OP(">="))
val andParser = TokenParser(T_OP("&&"))
val orParser = TokenParser(T_OP("||"))
val trueParser = TokenParser(T_KEYWORD("true"))
val falseParser = TokenParser(T_KEYWORD("false"))

// parser for simple statements
val skipParser = TokenParser(T_KEYWORD("skip"))
val assignParser = TokenParser(T_OP(":="))
val ifParser = TokenParser(T_KEYWORD("if"))
val thenParser = TokenParser(T_KEYWORD("then"))
val elseParser = TokenParser(T_KEYWORD("else"))
val whileParser = TokenParser(T_KEYWORD("while"))
val doParser = TokenParser(T_KEYWORD("do"))
val readParser = TokenParser(T_KEYWORD("read"))
val writeParser = TokenParser(T_KEYWORD("write"))

// parser for compound statements
val semiParser = TokenParser(T_SEMI)

// parser for blocks
val lcurlParser = TokenParser(T_PAREN("{"))
val rcurlParser = TokenParser(T_PAREN("}"))

// Abstract Syntax Trees
abstract class Stmt
abstract class AExp
abstract class BExp

type Block = List[Stmt]

case object Skip extends Stmt
case class If(a: BExp, bl1: Block, bl2: Block) extends Stmt
case class While(b: BExp, bl: Block) extends Stmt
case class Assign(s: String, a: AExp) extends Stmt
case class Read(s: String) extends Stmt
case class WriteId(s: String) extends Stmt  // for printing values of variables
case class WriteString(s: String) extends Stmt  // for printing words

case class Var(s: String) extends AExp
case class Num(i: Int) extends AExp
case class Aop(o: String, a1: AExp, a2: AExp) extends AExp

case object True extends BExp
case object False extends BExp
case class Bop(o: String, a1: AExp, a2: AExp) extends BExp
case class Lop(o: String, b1: BExp, b2: BExp) extends BExp
                 

// Parser rules

// arithmetic expressions
lazy val AExp: Parser[List[Token], AExp] = 
  (Te ~ plusParser ~ AExp).map[AExp]{ case ((x, _), z) => Aop("+", x, z) } ||
  (Te ~ minusParser ~ AExp).map[AExp]{ case ((x, _), z) => Aop("-", x, z) } || Te
lazy val Te: Parser[List[Token], AExp] = 
  (Fa ~ mulParser ~ Te).map[AExp]{ case ((x, _), z) => Aop("*", x, z) } ||
  (Fa ~ divParser ~ Te).map[AExp]{ case ((x, _), z) => Aop("/", x, z) } ||
  (Fa ~ modParser ~ Te).map[AExp]{ case ((x, _), z) => Aop("%", x, z) } || Fa
lazy val Fa: Parser[List[Token], AExp] =
  (lparenParser ~ AExp ~ rparenParser).map[AExp]{ case ((_, y), _) => y } || 
  IdParser.map(Var(_)) ||
  NumParser.map(Num(_))

// boolean expressions
lazy val BExp: Parser[List[Token], BExp] = 
  (AExp ~ eqParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop("==", x, y) } ||
  (AExp ~ neqParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop("!=", x, y) } ||
  (AExp ~ ltParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop("<", x, y) } ||
  (AExp ~ gtParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop(">", x, y) } ||
  (AExp ~ leParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop("<=", x, y) } ||
  (AExp ~ geParser ~ AExp).map[BExp]{ case ((x, _), y) => Bop(">=", x, y) } ||
  (lparenParser ~ BExp ~ rparenParser ~ andParser ~ BExp).map[BExp]{ case ((((_, y), _), _), v) => Lop("&&", y, v) } ||
  (lparenParser ~ BExp ~ rparenParser ~ orParser ~ BExp).map[BExp]{ case ((((_, y), _), _), v) => Lop("||", y, v) } ||
  (trueParser.map[BExp]{ _ => True }) ||
  (falseParser.map[BExp]{ _ => False }) ||
  (lparenParser ~ BExp ~ rparenParser).map[BExp]{ case ((_, x), _) => x }

// simple statements compund statements and blocks
lazy val Stmt: Parser[List[Token], Stmt] = 
  (skipParser.map[Stmt]{ _ => Skip }) ||
  (IdParser ~ assignParser ~ AExp).map[Stmt]{ case ((x, _), z) => Assign(x, z) } ||
  (ifParser ~ BExp ~ thenParser ~ Block ~ elseParser ~ Block).map[Stmt]{ case (((((_, y), _), u), _), w) => If(y, u, w) } ||
  (whileParser ~ BExp ~ doParser ~ Block).map[Stmt]{ case (((_, y), _), u) => While(y, u) } ||
  (writeParser ~ IdParser).map[Stmt]{ case (_, x) => WriteId(x) } ||
  (writeParser ~ lparenParser ~ IdParser ~ rparenParser).map[Stmt]{ case (((_, _), x), _) => WriteId(x) } ||
  (writeParser ~ StringParser).map[Stmt]{ case (_, x) => WriteString(x) } ||
  (writeParser ~ lparenParser ~ StringParser ~ rparenParser).map[Stmt]{ case (((_, _), x), _) => WriteString(x) } ||
  (readParser ~ IdParser).map[Stmt]{ case (_, x) => Read(x) }
lazy val Stmts: Parser[List[Token], Block] = 
  (Stmt ~ semiParser ~ Stmts).map[Block]{ case ((x, _), y) => x :: y } ||
  (Stmt.map[Block]{ x => List(x) })
lazy val Block: Parser[List[Token], Block] = 
  ((lcurlParser ~ Stmts ~ rcurlParser).map { case ((_, y), _) => y } || 
  (Stmt.map(x => List(x))))

// Interpreter
//=============

// Import needed to take an int as input from the user
import scala.io.StdIn.readInt

type Env = Map[String, Int]

def eval_aexp(a: AExp, env: Env) : Int = a match {
  case Var(x) => env(x)
  case Num(n) => n
  case Aop("+", a1, a2) => eval_aexp(a1, env) + eval_aexp(a2, env)
  case Aop("-", a1, a2) => eval_aexp(a1, env) - eval_aexp(a2, env)
  case Aop("*", a1, a2) => eval_aexp(a1, env) * eval_aexp(a2, env)
  case Aop("/", a1, a2) => eval_aexp(a1, env) / eval_aexp(a2, env)
  case Aop("%", a1, a2) => eval_aexp(a1, env) % eval_aexp(a2, env)
}

def eval_bexp(b: BExp, env: Env) : Boolean = b match {
  case True => true
  case False => false
  case Bop("==", a1, a2) => eval_aexp(a1, env) == eval_aexp(a2, env)
  case Bop("!=", a1, a2) => eval_aexp(a1, env) != eval_aexp(a2, env)
  case Bop("<", a1, a2) => eval_aexp(a1, env) < eval_aexp(a2, env)
  case Bop(">", a1, a2) => eval_aexp(a1, env) > eval_aexp(a2, env)
  case Bop("<=", a1, a2) => eval_aexp(a1, env) <= eval_aexp(a2, env)
  case Bop(">=", a1, a2) => eval_aexp(a1, env) >= eval_aexp(a2, env)
  case Lop("&&", b1, b2) => eval_bexp(b1, env) && eval_bexp(b2, env)
  case Lop("||", b1, b2) => eval_bexp(b1, env) || eval_bexp(b2, env)
}

def eval_stmt(s: Stmt, env: Env) : Env = s match {
  case Skip => env
  case Assign(x, a) => env + (x -> eval_aexp(a, env))
  case Read(x) => env + (x -> readInt())
  case WriteId(x) => print(env(x)); env
  case WriteString(s) => print(s.replace("\"", "").replace("\\n", "\n")); env
  case If(b, bl1, bl2) => 
    if (eval_bexp(b, env)) eval_bl(bl1, env) else eval_bl(bl2, env)
  case While(b, bl) => 
    if (eval_bexp(b, env)) eval_stmt(While(b, bl), eval_bl(bl, env))
    else env
}
def eval_bl(bl: Block, env: Env) : Env = bl match {
  case Nil => env
  case s::ss => eval_bl(ss, eval_stmt(s, env))
}

// main eval function for the interpreter
def eval(bl: Block) : Env = eval_bl(bl, Map())

@main
def test(file: String) = {
  val contents = os.read(os.pwd / "examples" / file)
  println(s"Lex $file: ")
  val tks = tokenise(contents)
  println(tks.mkString(","))
  println(s"Parse $file: ")
  val ast = Stmts.parse_all(tks).head
  println(ast)
  println(s"Eval $file: ")
  println(eval(ast))
}