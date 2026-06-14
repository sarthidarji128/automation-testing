describe('DELETE Message API Test', () => {
  it('successfully recalls/deletes a message', () => {
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

    const uniqueMsg = `Msg to delete ${Date.now()}`;
    cy.get('#message-input').should('be.visible').clear().type(uniqueMsg);
    cy.get('.message-input-bar .fa-paper-plane').should('be.visible').click();

    cy.get('.message-list').should('contain', uniqueMsg);

    // Hover or trigger actions for last message
    cy.get('.msg-row.sent').last().within(() => {
      cy.get('.msg-caret-btn').click({ force: true });
    });

    cy.get('.msg-dropdown.active').should('be.visible');
    
    // Handle alert prompt/confirm popups automatically
    cy.on('window:confirm', () => true);
    
    cy.get('.msg-dropdown.active .msg-dropdown-item.danger').contains('Delete for all').click();

    // Verify it is gone
    cy.get('.message-list').should('not.contain', uniqueMsg);
  });
});
