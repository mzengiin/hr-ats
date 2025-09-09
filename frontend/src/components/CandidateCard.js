import React from 'react';
import './CandidateCard.css';

const CandidateCard = ({ candidate, onClick }) => {
  return (
    <div className="candidate-card" onClick={onClick}>
      <div className="candidate-header">
        <div className="candidate-avatar">
          {candidate.avatar}
        </div>
        <div className="candidate-info">
          <h4>{candidate.name}</h4>
          <p className="position">{candidate.position}</p>
        </div>
      </div>
      <div className="skills">
        {candidate.skills.map((skill, index) => (
          <span key={index} className="skill-tag">{skill}</span>
        ))}
      </div>
    </div>
  );
};

export default CandidateCard;

