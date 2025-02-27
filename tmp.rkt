#lang rosette

(require rosette/lib/synthax)

(define BV_SIZE 64)

; the bitvector type
(define int? (bitvector BV_SIZE))
(define (int i)
  (bv i BV_SIZE))

; specification
; note: the translation for llvm ne should be (not (bveq reg1 reg2))
(define (check impl %tmp_alter1 %reg2)
  (define result (impl %tmp_alter1 %reg2))
  (assert (bveq result (bvxor %reg2 %reg2)))) 


; construct the grammar template
; note: there are no unary operations in llvm, so we do not model them here
(define-grammar (binop_int %tmp_alter1 %reg2)
  [expr
    (choose %tmp_alter1 %reg2 (?? int?)
        ((bop) (expr) (expr)))]
  [bop
    (choose bveq bvlshr bvsub bvmul bvadd bvshl bvor bvand bvashr)])
  

; expand the grammar template with depth
(define (alter_op %tmp_alter1 %reg2)
  (binop_int %tmp_alter1 %reg2 #:depth 2))

; synthesize
(define-symbolic l r int?)

(define sol
  (synthesize
    #:forall    (list l r)
    #:guarantee (check alter_op l r)))

; print the alternative expression if `sat`, otherwise print #f
(if (sat? sol) (print-forms sol) #f)