import './modal.css';
import React, {Component} from 'react';

const Modal = (props) => {
    if (!props.show) {
        return null;
    }
    return (
        <div className = 'modal'>
            <div className = 'modal-content'>
                <div className = 'modal-header'>
                    {/* <h4 className = 'modal-title'>Modal title</h4> */}
                </div>
                <div className = 'modal-body'>
                    User has acknowledged the privacy policy.
                </div>
                <div className = 'modal-footer'>
                    <button onClick= {props.onClose} className = 'button'>Close</button>
                </div>
            </div>
        </div>
    );
};

export default Modal;
