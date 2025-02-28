#lang rosette

(require rosette/lib/synthax)

(define BV_SIZE 32)

; the bitvector type
(define int? (bitvector BV_SIZE))
(define (int i)
  (bv i BV_SIZE))

; specification
; note: the translation for llvm ne should be (not (bveq reg1 reg2))
(define (check impl %48 %49)
  (define result (impl %48 %49))
  (assert (bveq result (bvxor %48 %49)))) 


; construct the grammar template
; note: there are no unary operations in llvm, so we do not model them here
(define-grammar (binop_int %48 %49)
  [expr
    (choose %48 %49 (?? int?)
        ((bop) (expr) (expr)))]
  [bop
    (choose bvadd bvashr bvsub bvand bvor bvlshr bvshl bveq bvmul)])
  

; expand the grammar template with depth
(define (alter_op %48 %49)
  (binop_int %48 %49 #:depth 2))

; synthesize
(define-symbolic l r int?)

(define sol
  (synthesize
    #:forall    (list l r)
    #:guarantee (check alter_op l r)))

; print the alternative expression if `sat`, otherwise print #f
(if (sat? sol) (print-forms sol) #f)