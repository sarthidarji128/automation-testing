describe('POST Message API Test', () => {
  it('successfully transmits a message to a partner', () => {
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

    const uniqueMsg = `Hello Bob! Automated test ${Date.now()}`;
    
    cy.get('#message-input').should('be.visible').clear().type(uniqueMsg);
    cy.get('.message-input-bar .fa-paper-plane').should('be.visible').click();

    // Verify message bubble is rendered in chat list (shows it was successfully posted)
    cy.get('.message-list').should('contain', uniqueMsg);
  });
});
