#!/usr/bin/env amm
import $ivy.`org.scalatest::scalatest::3.2.9`
import $ivy.`com.lihaoyi::os-lib:0.7.8`

import org.scalatest.funsuite.AnyFunSuite
import os._

import $file.^.scala_code.lexer, lexer._

object TestLexer extends AnyFunSuite {

  // Read the input file (e.g., collatz.while) from the examples folder
  val collatz_while = os.read(os.Path("/Users/muhammad/Desktop/Dissertation/Muthallajat/examples/collatz.while"))

  test("Lex collatz.while") {
    println("Lex collatz.while: ")
    val tokens = tokenise(collatz_while)
    val expectedTokens = List(
      T_KEYWORD("write"), T_STRING("Input a number "), T_SEMI,
      T_KEYWORD("read"), T_ID("n"), T_SEMI,
      T_KEYWORD("while"), T_ID("n"), T_OP(">"), T_NUM(1), T_KEYWORD("do"), T_PAREN("{"),
      T_KEYWORD("if"), T_ID("n"), T_OP("%"), T_NUM(2), T_OP("=="), T_NUM(0), T_KEYWORD("then"),
      T_ID("n"), T_OP(":="), T_ID("n"), T_OP("/"), T_NUM(2),
      T_KEYWORD("else"), T_ID("n"), T_OP(":="), T_NUM(3), T_OP("*"), T_ID("n"), T_OP("+"), T_NUM(1),
      T_PAREN("}"), T_SEMI,
      T_KEYWORD("write"), T_STRING("Yes\n")
    )
    if (tokens != expectedTokens) {
      println(s"Expected: $expectedTokens, but got: $tokens")
      assert(false)
    } else {
      assert(true)
    }
  }
}

// Execute the tests
TestLexer.execute()