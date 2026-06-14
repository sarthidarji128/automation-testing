describe('PUT Message API Test', () => {
  it('successfully edits an existing message', () => {
    cy.request('GET', '/api/state').then((response) => {
      const state = response.body || {};
      cy.request('POST', '/api/state', { ...state, currentUser: null });
    });

    cy.visit('/#/login');
    cy.get('#login-username').should('be.visible').clear().type('alice');
    cy.get('#login-password').should('be.visible').clear().type('123');
    cy.get('#login-form .auth-btn').click();

    cy.url().should('include', '/#/chat');
    
    // Switch to Users to find Bob
    cy.get('#tab-users').should('be.visible').click();
    cy.get('.list-item').contains('Bob').click();

    const uniqueMsg = `Msg to edit ${Date.now()}`;
    cy.get('#message-input').should('be.visible').clear().type(uniqueMsg);
    cy.get('.message-input-bar .fa-paper-plane').should('be.visible').click();

    cy.get('.message-list').should('contain', uniqueMsg);

    // Hover or trigger actions for last message
    cy.get('.msg-row.sent').last().within(() => {
      // Show caret by invoking dropdown trigger
      cy.get('.msg-caret-btn').click({ force: true });
    });

    cy.get('.msg-dropdown.active').should('be.visible');
    cy.get('.msg-dropdown.active .msg-dropdown-item').contains('Edit message').click();

    const editedText = `This message was edited ${Date.now()}`;
    cy.get('.msg-edit-input').clear().type(editedText);
    cy.get('.msg-edit-btn.save').click();

    // Verify it is updated
    cy.get('.message-list').should('contain', editedText);
    cy.get('.message-list').should('not.contain', uniqueMsg);
  });
});
