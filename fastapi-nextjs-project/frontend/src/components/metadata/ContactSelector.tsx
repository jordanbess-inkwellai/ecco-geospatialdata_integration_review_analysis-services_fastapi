import React, { useState } from 'react';

interface Contact {
  id?: number;
  name: string;
  organization?: string;
  email?: string;
  role?: string;
  [key: string]: any;
}

interface ContactSelectorProps {
  contacts: Contact[];
  availableContacts: Contact[];
  onChange: (contacts: Contact[]) => void;
}

export const ContactSelector: React.FC<ContactSelectorProps> = ({
  contacts = [],
  availableContacts = [],
  onChange
}) => {
  // State for new contact form
  const [showNewContactForm, setShowNewContactForm] = useState(false);
  const [newContact, setNewContact] = useState<Contact>({
    name: '',
    organization: '',
    email: '',
    role: 'pointOfContact'
  });
  
  // Handle adding an existing contact
  const handleAddExistingContact = (contactId: number, role: string = 'pointOfContact') => {
    const contact = availableContacts.find(c => c.id === contactId);
    
    if (contact) {
      const updatedContacts = [
        ...contacts,
        { ...contact, role }
      ];
      
      onChange(updatedContacts);
    }
  };
  
  // Handle adding a new contact
  const handleAddNewContact = () => {
    if (!newContact.name) return;
    
    const updatedContacts = [
      ...contacts,
      { ...newContact }
    ];
    
    onChange(updatedContacts);
    
    // Reset form
    setNewContact({
      name: '',
      organization: '',
      email: '',
      role: 'pointOfContact'
    });
    
    setShowNewContactForm(false);
  };
  
  // Handle removing a contact
  const handleRemoveContact = (index: number) => {
    const updatedContacts = [...contacts];
    updatedContacts.splice(index, 1);
    onChange(updatedContacts);
  };
  
  // Handle changing contact role
  const handleChangeRole = (index: number, role: string) => {
    const updatedContacts = [...contacts];
    updatedContacts[index] = { ...updatedContacts[index], role };
    onChange(updatedContacts);
  };
  
  // Filter available contacts to exclude already selected ones
  const filteredAvailableContacts = availableContacts.filter(
    availableContact => !contacts.some(
      contact => contact.id === availableContact.id
    )
  );
  
  return (
    <div className="contact-selector">
      <div className="selected-contacts">
        {contacts.length === 0 ? (
          <div className="no-contacts">No contacts added</div>
        ) : (
          <ul className="contact-list">
            {contacts.map((contact, index) => (
              <li key={index} className="contact-item">
                <div className="contact-info">
                  <div className="contact-name">{contact.name}</div>
                  {contact.organization && (
                    <div className="contact-organization">{contact.organization}</div>
                  )}
                  {contact.email && (
                    <div className="contact-email">{contact.email}</div>
                  )}
                </div>
                
                <div className="contact-actions">
                  <select
                    value={contact.role || 'pointOfContact'}
                    onChange={(e) => handleChangeRole(index, e.target.value)}
                    className="role-select"
                  >
                    <option value="pointOfContact">Point of Contact</option>
                    <option value="custodian">Custodian</option>
                    <option value="owner">Owner</option>
                    <option value="user">User</option>
                    <option value="distributor">Distributor</option>
                    <option value="originator">Originator</option>
                    <option value="principalInvestigator">Principal Investigator</option>
                    <option value="processor">Processor</option>
                    <option value="publisher">Publisher</option>
                    <option value="author">Author</option>
                  </select>
                  
                  <button
                    type="button"
                    className="remove-button"
                    onClick={() => handleRemoveContact(index)}
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="add-contact">
        {showNewContactForm ? (
          <div className="new-contact-form">
            <h4>Add New Contact</h4>
            
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={newContact.name}
                onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                className="form-control"
                placeholder="Contact name"
              />
            </div>
            
            <div className="form-group">
              <label>Organization</label>
              <input
                type="text"
                value={newContact.organization || ''}
                onChange={(e) => setNewContact({ ...newContact, organization: e.target.value })}
                className="form-control"
                placeholder="Organization"
              />
            </div>
            
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={newContact.email || ''}
                onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
                className="form-control"
                placeholder="Email address"
              />
            </div>
            
            <div className="form-group">
              <label>Role</label>
              <select
                value={newContact.role}
                onChange={(e) => setNewContact({ ...newContact, role: e.target.value })}
                className="form-control"
              >
                <option value="pointOfContact">Point of Contact</option>
                <option value="custodian">Custodian</option>
                <option value="owner">Owner</option>
                <option value="user">User</option>
                <option value="distributor">Distributor</option>
                <option value="originator">Originator</option>
                <option value="principalInvestigator">Principal Investigator</option>
                <option value="processor">Processor</option>
                <option value="publisher">Publisher</option>
                <option value="author">Author</option>
              </select>
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowNewContactForm(false)}
              >
                Cancel
              </button>
              
              <button
                type="button"
                className="add-button"
                onClick={handleAddNewContact}
                disabled={!newContact.name}
              >
                Add Contact
              </button>
            </div>
          </div>
        ) : (
          <div className="add-contact-options">
            {filteredAvailableContacts.length > 0 && (
              <div className="existing-contacts">
                <select
                  className="contact-select"
                  onChange={(e) => {
                    if (e.target.value) {
                      handleAddExistingContact(parseInt(e.target.value));
                      e.target.value = '';
                    }
                  }}
                >
                  <option value="">Select an existing contact</option>
                  {filteredAvailableContacts.map(contact => (
                    <option key={contact.id} value={contact.id}>
                      {contact.name} {contact.organization ? `(${contact.organization})` : ''}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <button
              type="button"
              className="new-contact-button"
              onClick={() => setShowNewContactForm(true)}
            >
              Add New Contact
            </button>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .contact-selector {
          margin-bottom: 1rem;
        }
        
        .selected-contacts {
          margin-bottom: 1rem;
        }
        
        .no-contacts {
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
          text-align: center;
          color: #666;
          font-style: italic;
        }
        
        .contact-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .contact-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #f8f9fa;
          border-radius: 4px;
          margin-bottom: 0.5rem;
        }
        
        .contact-info {
          flex: 1;
        }
        
        .contact-name {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }
        
        .contact-organization, .contact-email {
          font-size: 0.9rem;
          color: #666;
        }
        
        .contact-actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .role-select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .remove-button {
          background-color: #f8d7da;
          color: #721c24;
          border: none;
          border-radius: 4px;
          padding: 0.5rem;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .add-contact-options {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }
        
        .existing-contacts {
          flex: 1;
        }
        
        .contact-select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .new-contact-button {
          background-color: #e9ecef;
          color: #333;
          border: 1px solid #ddd;
          border-radius: 4px;
          padding: 0.75rem 1rem;
          font-size: 0.9rem;
          cursor: pointer;
          white-space: nowrap;
        }
        
        .new-contact-form {
          background-color: #f8f9fa;
          border-radius: 4px;
          padding: 1rem;
        }
        
        .new-contact-form h4 {
          margin-top: 0;
          margin-bottom: 1rem;
          font-size: 1.1rem;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          font-size: 0.9rem;
        }
        
        .form-control {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.5rem;
          margin-top: 1rem;
        }
        
        .cancel-button, .add-button {
          padding: 0.5rem 1rem;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
        }
        
        .cancel-button {
          background-color: #f8f9fa;
          color: #333;
          border: 1px solid #ddd;
        }
        
        .add-button {
          background-color: #0070f3;
          color: white;
          border: none;
        }
        
        .add-button:disabled {
          background-color: #ccc;
          cursor: not-allowed;
        }
        
        @media (max-width: 768px) {
          .contact-item {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .contact-actions {
            margin-top: 1rem;
            width: 100%;
          }
          
          .role-select {
            flex: 1;
          }
          
          .add-contact-options {
            flex-direction: column;
          }
          
          .existing-contacts {
            width: 100%;
            margin-bottom: 0.5rem;
          }
          
          .new-contact-button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default ContactSelector;
