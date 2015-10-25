# LISP on TeX #

A LISP interpreter written only with TeX macros.
It works as a style file of LaTeX.
LISP on TeX adopts static scoping, dynamic typing, and eager evaluation.
We can program easily with LISP on TeX.

## Summary ##

To use LISP on TeX, you should include the `lisp-on-tex` package.
```
\usepackage{lisp-on-tex}
```

If you do it, you can write LISP codes as a argument of `\lispinterp`.
```
\lispintrep{
  (\some \LISP 'codes')
  % example
  (\define (\sum \a \b) (\+ \a \b))
}
```

In LISP on TeX, a symbol is a control sequence;
a string is tokens surrounded by quotation marks;
and an integer is a TeX's integer using colon prefix.

## Installation ##

Put all files into your TEXMF tree.


## Details ##

### Class Options ###

| Option Name | Meaning                         |
| ----------- | ------------------------------- |
| `noGC`      | Never using GC (default)        |
| `markGC`    | Using Mark-Sweep GC             |
| `GCopt=...` | Passing option to the GC engine |

Currently, LISP on TeX supports Mark-Sweep GC.
If you want to use it, you should use `markGC` option.
You can also control heap size by using `GCopt={heapsize=n}`
where `n` is greater than 3000. The default heap size is 32768.
For example, the code
```
\usepackage[markGC, GCopt={heapsize=5000}]{lisp-on-tex}
```
shows that LISP on TeX uses Mark-Sweep GC and the heap size is 5000.

### Syntax ###

| Kinds              | Literals                                       | Examples         |
| ------------------ | ---------------------------------------------- | ---------------- |
| CONS Cell          | `(` *obj* ... `.` *obj* `)`, `(` *obj* ... `)` | `(\+ :1 :2)`     |
| Integer            | `:` *TeX's integer*                            | `:42`, `:"3A`    |
| String             | `'` *TeX's balanced tokens* `'`                | `'\foo{bar}baz'` |
| Symbol             | *TeX's control sequence*                       | `\cs`            |
| Boolean            | `/t` or `/f`                                   |                  |
| Nil                | `()`                                           |                  |
| Skip               | `@` *TeX's skip*                               | `@12pt plus 34cm`|
| Dimen              | `!` *TeX's dimen*                              | `!56pt`          |

### Functions and Special Forms ###

#### Definition ####

`\define` : Define a symbol.
************************************

```
% symbol form
(\define \foo :42) % ()
\foo % :42
% function form
(\define (\foo \n) (\* \n :2))
(\foo :3) % :6
```

`\defineM` : Define a mutable symbol.
*************************************
`\setB` : Rewrite a mutable symbol.
*************************************

```
% symbol form
(\defineM \foo :42) % ()
\foo % :42
(\setB \foo 'bar')
\foo % 'bar'
```

`\defmacro` : Define a macro.
*************************************
`\macroexpand` : Expand a macro
*************************************

```
(\defmacro (\foo \x) (\list (\quote \bar) \x \x \x)) % ()
(\macroexpand (\quote (\foo :1))) % (\bar :1 :1 :1)
```


`\lambda` : Create a function.
**************************************

```
% normal form
((\lambda (\x) (\+ \x :2)) :3) % :5
% list form
((\lambda \x \x) :1 :2) % (:1 :2)
% remain argument form
((\lambda (\x . \y) \y) :1 :2 :3) % (:2 :3)
```

`\let` : Define local symbols.
*****************************************

```
(\define \x 'foo')
(\let ((\x :4) (\y :3)) (\+ \x \y)) % :7
\x % 'foo'
```

`\letM` : Define mutable local symbols.
******************************************

```
(\letM ((\x 'foo'))
  (\begin (\setB \x 'bar') \x)) % 'bar'
```

`\letrec` : Define local symbols recursively.
********************************************

```
(\letrec
  ((\oddQ (\lambda (\n)
             (\lispif (\= \n :0) /f (\evenQ (\- \n :1)))))
   (\evenQ (\lambda (\n)
             (\lispif (\= \n :0) /t (\oddQ (\- \n :1))))))
   (\oddQ :42)) % /f
```

#### Control Flow ####

`\lispif` : Branch.
********************************************

```
(\lispif /t 'true' 'false') % 'true'
(\lispif /f 'true' 'false') % 'false'
```

`\begin` : Execute expressions.
********************************************

```
(\letM ((\x :1)) (\begin (\setB \s 'foo') \x))
% 'foo'
```

`\callOCC` : One-shot continuation.
*******************************************

```
(\defineM \x 'unchanged')
(\callOCC (\lambda (\c)
             (\begin (\c '\foo ')
                     (\setB \x 'changed')))) % '\foo '
\x % 'unchanged'
(\callOCC (\lambda (\c) :42)) % :42
```

#### String Manipulations ####

`\concat` : Concatenate tokens.
************************************

```
(\concat '$' '\foo ' '{bar}' '$') % '$\foo {bar}$'
```

`\intTOstring` : Convert a integer to TeX's tokens.
******************************************************

```
(\intTOstring :42) % '42'
```

`\group` : Grouping.
*******************************

```
(\group '\some {tokens}') % '{\some {tokens}}'
```

`\ungroup` : Ungrouping.
************************

```
(\ungroup '{\some {tokens}}') % '\some {tokens}' 
```

`\expand` : Expand tokens.
******************************

```
\newcommand\foo[1]{I got #1!}
\lispinterp{
  (\expand '\foo{Foo}') % 'I got Foo!'
}
```

#### Arithmetical Functions ####

`\+` : Addition.
***************************

```
(\+) % :0
(\+ :1 :2) % :3
(\+ :3 :4 :5) % :12
```

`\-` : Subtraction.
************************

```
(\- :1) % :-1
(\- :3 :2) % :1
(\- :3 :2 :1) % :0
```

`\*` : Multiplication.
**********************

```
(\*) % :1
(\* :2 :3) % :6
(\* :3 :4 :5) % :60
```

`\/` : Division.
*************************

```
(\/ 2) % :0 (1/2 -> 0)
(\/ 7 2) % :3
```

`\mod` : Modulo.
*************************

```
(\mod :42 :23)  % :19
(\mod :3 :2)    % :1
(\mod :3 :-2)   % :1
(\mod :-3 :2)   % :-1
(\mod :-3 :-2)  % :-1
```

`\>`, `\<`, `\geq`, `\leq` : Comparison.
*******************************************

```
(\> :3 :2)   % /t
(\< :2 :3)   % /t
(\geq :3 :2) % /t
(\geq :3 :3) % /t
(\leq :2 :3) % /t
(\leq :3 :3) % /t
```

Some predicates.
************************

```
(\isZeroQ :0)    % /t
(\positiveQ :42) % /t
(\negativeQ :-2) % /t
```

`\max` : Maximum.
***************************

```
(\max :-10 :-5 :0 :5 :10) % :10
```

`\min` : Minimum.
*****************************

```
(\min :-10 :-5 :0 :5 :10) % :-10
```

#### Logical functions ####

`\and`, `\or`, `\not` : Logical and, or, not
*********************************************

```
(\and /t /t) % /t
(\and /t /f) % /f
(\or /t /t)  % /t
(\or /t /f)  % /t
(\not /t)    % /f
```


#### Traditional LISP Functions and Special Forms ####

`\quote` : Quote.
*******************

```
(\quote :42) % :42
(\quote (\+ :1 :2)) % (\+ :1 :2)
```

`\cons`, `\car`, `\cdr` : CONS, CAR, CDR
*************************************

```
(\cons :42 'foo') % (:42 . 'foo')
(\car (\quote (:1 :2))) % :1
(\cdr (\quote (:1 :2))) % (:2)
```

`\list` : Create a list
***************************

```
(\list :1 :2 (\+ :3 :4)) % (:1 :2 :7)
```

`\length` : Get the length of a list.
*****************************************

```
(\length ()) % :0
(\length (\list :1 :2 'three')) % :3
```

`\map` : Map function.
**************************

```
(\define (\f \x \y \z) (\+ \x \y \z))
(\map \f (\list :1 :2 :3)
         (\list :4 :5 :6)
         (\list :7 :8 :9)) % (:12 :15 :18)
```

`\nth` : Get the n-th value of a list (starting with 0).
***********************************************************

```
(\nth (\list 'foo' 'bar' 'baz') :1) % 'bar'
```


`\=` : Equality.
*******************

```
(\= '42' :42) % /f
(\= :23 :23) % /t
(\= (\cons :1 'foo') (\cons :1 'foo')) % /f
(\= 'foo' 'foo') % /t
```
`\texprint` : Convert a object to TeX's tokens and output it to the document
******************************************************************************

```
(\texprint (\concat '\foo' (\group '42'))) % return () andoutput \foo{42}
(\texprint :42) % output 42
```

`\print` : (For test) output a object as TeX's tokens
*******************************************************

```
(\print ()) % output ()
(\print (\quote \foo)) % output \string\foo
(\print :42) % output :42
(\print 'bar') % output 'bar'
```

Type predicates
*********************

```
(\symbolQ (\quote \cs))
(\stringQ 'foo')
(\intQ :42)
(\booleanQ /f)
(\dimenQ !12pt)
(\skipQ @12pt plus 1in minus 3mm)
(\pairQ (\cons :1 :2))
(\nilQ ())
(\funcQ \+)
(\closureQ (\lambda () ()))
(\defmacro (\x) ())
(\macroQ \x)
(\listQ ())
(\listQ (\list :1 :2))
(\atomQ :23)
(\atomQ 'bar')
(\procedureQ \+)
(\procedureQ (\lambda () ()))
```

#### LaTeX Utils ####

`\readLaTeXCounter` : Read an integer from LaTeX
***************************************************

```
\setcounter{foo}{42}
\lispinterp{
  (\readLaTeXCounter 'foo') % :42
}
```

`\message` : Wrapper of LaTeX's \message
*******************************************

```
(\message 'output') % output "message" to console and return ()
```

#### Others ####

`\read` : Read a LISP expression from stdin
*********************************************

```
(\read) % input :42 and return it
```

`\fgets` : Read a string from stdin.
***************************************

```
(\fgets) % input \some {tokens} and return '\some {tokens}'
```


##Additional Packages ##

### Fixed Point Numbers ###

The package lisp-mod-fpnum adds fixed point numbers
to LISP on TeX. Load it by `\usepackage`:

```
\usepackage{lisp-on-tex}
\usepackage{lisp-mod-fpnum}
```

#### Syntax ####

| Kinds              | Literals                                       | Examples         |
| ------------------ | ---------------------------------------------- | ---------------- |
| Fixed point number | `+{fpnum::` *number* `}`                       | `+{fpnum::1.23}` |

#### Functions ####

`\fpnumTOstring` : Convert a fixed point number to a string.
************************************************************

```
(\fpnumTOstring +{fpnum::1.23}) % '1.23'
```

`\fpplus` : Addition.
*********************

```
(\fpplus +{fpnum::1.2} +{fpnum::1.4}) % 2.59999 (arithmetical error)
```

`\fpminus` : Subtraction.
************************

```
(\fpminus +{fpnum::4.2} +{fpnum::2.3}) % 1.9
```

`\fpmul` : Multiplication.
*****************************

```
(\fpmul +{fpnum::1.2} +{fpnum::1.4}) % 1.67998
```

`\fplt` : Comparison.
**************************

```
(\fplt +{fpnum::1.2} +{fpnum::2.3}) % /t
```


### Regular Expressions ###

The package lisp-mod-l3regex is thin wrapper
of l3regex. Load it by `\usepackage`:

```
\usepackage{lisp-on-tex}
\usepackage{lisp-mod-l3regex}
```

#### Functions ####

`\regMatch`, `\regMatchResult` : Match.
*************************************

```
(\regMatch 'hoge+' 'hogeeeeeee') % /t
(\regMatchResult '(\w+)\s+is\s+(\w+)\.' 'He is crazy.')
% ('He is crazy.' 'He' 'crazy')
```

`\regExtract` : Extraction.
****************************

```
(\regExtract '\w+' 'hello regex world') % ('hello' 'regex' 'world')
```

`\regReplaceAll`, `\regReplaceOnce` : Replace.
**********************************************

```
(\regReplaceAll '(\w+?)to(\w+?)' '$\1\c{to}\2$' 'AtoB BtoC') % '$A\to B$ $B\to C$'
(\regReplaceOnce 'foo+' '[\0]' 'foooofooooooo') % '[foooo]fooooooo'
```

`\regSplit` : Split.
***********************

```
(\regSplit '/' '/path/to/hogehoge') % ('' 'path' 'to' 'hogehoge')
```


## TODOs ##

* Writing user manual
* Add functions and special forms

## CHANGELOG ##

Oct. 25, 2015 : 2.0
*************************

* Add GC
* Refine some special forms like \define
* Add checking #args for some functions.
* Add thin wrapper of l3regex

Jul. 12, 2014 : 1.3
*************************

* Add one shot continuations.
* Add some arithmetical functions.
* Debug environment.

Jan. 03, 2014 : 1.2
**************************

* Added TUG2013's examples.
* Improved the performance.

Aug. 10, 2013 : 1.1
**************************

* Added \letrec and \expand.
* debug

Mar. 04, 2013 : 1.0
**************************

## Licence ##

Modified BSD (see LICENCE)

************************************************
HAKUTA Shizuya <hak7a3@live.jp>

https://bitbucket.org/hak7a3/lisp-on-tex/
