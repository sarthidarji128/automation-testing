describe('GET Users API Test', () => {
  it('successfully fetches and renders the user directory list', () => {
    // Reset currentUser to login
    cy.request('GET', '/api/state').then((response) => {
      const state = response.body || {};
      cy.request('POST', '/api/state', { ...state, currentUser: null });
    });

    cy.visit('/#/login');
    cy.get('#login-username').should('be.visible').clear().type('alice');
    cy.get('#login-password').should('be.visible').clear().type('123');
    cy.get('#login-form .auth-btn').click();

    cy.url().should('include', '/#/chat');
    
    // Switch to "All Users" tab (GET /api/users is called)
    cy.get('#tab-users').should('be.visible').click();
    
    // Check that user items are rendered
    cy.get('.list-item').should('have.length.at.least', 1);
    cy.get('.item-name').should('be.visible');
  });
});
