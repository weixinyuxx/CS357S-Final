#lang rosette

(require rosette/lib/synthax)

(define BV_SIZE 32); TODO: HOLE to fill

; the bitvector type
(define int? (bitvector BV_SIZE))
(define (int i)
  (bv i BV_SIZE))

; specification
; note: the translation for llvm ne should be (not (bveq reg1 reg2))
(define (check impl left right)
  (define result (impl left right))
  (assert (bveq result (bvadd left right)))) ; TODO: HOLE to fill, including constant

; construct the grammar template
; note: there are no unary operations in llvm, so we do not model them here
; TODO: to generate more equivalent expressions: delete used expressions from the bop list
(define-grammar (binop_int left right)
  [expr
    (choose left right (?? int?)
        ((bop) (expr) (expr)))]
  [bop
    (choose  bvsub bvmul
            bvshl bvlshr bvashr
            bvand bvor bvxor
            bveq)])
  

; expand the grammar template with depth
(define (alter_op left right)
  (binop_int left right #:depth 2))

; synthesize
(define-symbolic l r int?)

(define sol
  (synthesize
    #:forall    (list l r)
    #:guarantee (check alter_op l r)))

; print the alternative expression if `sat`, otherwise print #f
(if (sat? sol) (print-forms sol) #f)

; NOTE: uncomment to check the generated function
; (define (reverse-add left right)
;  (bvadd right left)) ; TODO: HOLE to fill, replace with the newly generated expression

; (define-symbolic r1 r2 int?)
; (define cex (verify (check-add reverse-add r1 r2)))
; cex


; TODO: a script to generate more alternative expressions (along with building the file from input)