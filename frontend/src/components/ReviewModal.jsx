import React, { useState } from 'react';
import { Star } from 'lucide-react';
import axios from 'axios';

const ReviewModal = ({ orderId, isOpen, onClose }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    try {
      await axios.post('/api/delivery/reviews', {
        order_id: orderId,
        rating,
        comment
      });
      setSubmitted(true);
      setTimeout(onClose, 2000);
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {submitted ? (
          <div className="success-message">
            <h3>¡Gracias por tu opinión! ⭐</h3>
          </div>
        ) : (
          <>
            <h3>Califica tu Pedido</h3>
            <div className="star-rating">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  size={32}
                  fill={star <= rating ? "#FFD700" : "none"}
                  color={star <= rating ? "#FFD700" : "#666"}
                  onClick={() => setRating(star)}
                  style={{ cursor: 'pointer' }}
                />
              ))}
            </div>
            <textarea
              placeholder="¿Qué tal estuvo la comida?"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="review-input"
            />
            <div className="modal-actions">
              <button onClick={onClose} className="btn btn-secondary">Cancelar</button>
              <button onClick={handleSubmit} className="btn btn-primary">Enviar</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ReviewModal;
