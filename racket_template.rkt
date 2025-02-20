#lang rosette

(require rosette/lib/synthax)

(define BV_SIZE {{ type }})

; the bitvector type
(define int? (bitvector BV_SIZE))
(define (int i)
  (bv i BV_SIZE))

; specification
; note: the translation for llvm ne should be (not (bveq reg1 reg2))
(define (check impl {{ left }} {{ right }})
  (define result (impl {{ left }} {{ right }}))
  (assert (bveq result {{ expr }}))) 


; construct the grammar template
; note: there are no unary operations in llvm, so we do not model them here
(define-grammar (binop_int {{ left }} {{ right }})
  [expr
    (choose {{ left }} {{ right }} (?? int?)
        ((bop) (expr) (expr)))]
  [bop
    (choose {{ rktop }})])
  

; expand the grammar template with depth
(define (alter_op {{ left }} {{ right }})
  (binop_int {{ left }} {{ right }} #:depth 2))

; synthesize
(define-symbolic l r int?)

(define sol
  (synthesize
    #:forall    (list l r)
    #:guarantee (check alter_op l r)))

; print the alternative expression if `sat`, otherwise print #f
(if (sat? sol) (print-forms sol) #f)
