import React, {useState} from 'react';
import Modal from './modal.jsx';

export default function PrivacyPolicy() {
  const [show, setShow] = useState(false);

  return (
    <div className = "Privacy Policy">
      <div>
        End-User License Agreement
      </div>
      <div>
        By clicking the I Agree button, downloading or using the application, you are agreeing to be bound by the terms and conditions of this agreement.
        If you do not agree to the terms of this agreement, do not click on the I Agree button, do not download or do not use the application. This agreement is a legal document between you and the company
        and it governs your use of the application made available to you by the company. This agreement is between you
        and the company only and not with the application store. Therefore, the company is solely
        responsible for the application and its content. Although the application store is not a party to this
        agreement, it has the right to enforce it against you as a third party
        beneficiary relating to your use of the application. Since the application can be
        accessed and used by other users via, for example, family sharing/family group or volume purchasing, the use
        of the application by those users is expressly subject to this agreement. The application
        is licensed, not sold to you by the company for use strictly in accordance with the
        terms of this agreement.
      </div>
      <button onClick = {() => setShow(true)}> I agree </button>
      <Modal onClose = {() => setShow(false)} show = {show}/>
    </div>
  );
}
