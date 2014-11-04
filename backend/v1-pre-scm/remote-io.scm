;;; Network I/O utilities.

(declare (usual-integrations))

(define (network-error)
  (error "Network error!"))

(define (call-with-tcp-server-socket service receiver)
  (let ((socket (open-tcp-server-socket service)))
    (begin0 (receiver socket)
      (close-port socket))))

(define (call-with-tcp-stream-socket host service receiver)
  (let ((socket (open-tcp-stream-socket host service)))
    (begin0 (receiver socket)
      (close-port socket))))

(define (call-with-accept-socket server-socket receiver)
  (let ((socket (listen-tcp-server-socket server-socket)))
    (begin0 (receiver socket)
      (close-port socket))))

(define hex-digits "0123456789abcdef")
(define char-set:hex (string->char-set hex-digits))

(define (network-read socket)
  (let* ((size-buf (make-string 6))
	 (size-n (read-substring! size-buf 0 6 socket)))
    (if (not (eqv? size-n 6))
	(network-error))
    (if (string-find-next-char-in-set size-buf (char-set-invert char-set:hex))
	(network-error))
    ;; XXX Use a safer parser than STRING->NUMBER.
    (let* ((size (string->number size-buf #x10))
	   (buf (make-string size))
	   (n (read-substring! buf 0 size socket)))
      (if (not (eqv? n size))
	  (network-error))
      ;; XXX Don't expose READ to the network.
      (read (open-input-string buf)))))

(define (network-write socket message)
  (let* ((buf (write-to-string message))
	 (size (string-length buf)))
    ;; XXX Hmm...  Assertion is sketchy here.
    (assert (<= size (expt 2 (* 6 4))))
    (let ((size-buf (make-string 6)))
      (let loop ((i 6) (s size))
	(if (< 0 i)
	    (let ((i (- i 1))
		  (h (string-ref hex-digits (bitwise-and s #xf))))
	      (string-set! size-buf i h)
	      (loop i (shift-right s 4)))))
      (let ((size-n (write-substring size-buf 0 6 socket)))
	(if (not (eqv? size-n 6))
	    (network-error))))
    (let ((n (write-substring buf 0 size socket)))
      (if (not (eqv? n size))
	  (network-error)))))
