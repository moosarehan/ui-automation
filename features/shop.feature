Feature: Student supply reservations
  Students sign in, find supplies and reserve a product for pickup.

  @login
  Scenario Outline: Sign in with the <account> account
    Given the shop is open
    When I sign in with Excel account "<account>"
    Then the status reads "<message>"

    Examples:
      | account | message          |
      | valid   | Welcome, student |
      | invalid | Sign-in failed   |

  @search
  Scenario Outline: Search the catalog using <case>
    Given I am a signed-in student
    When I search using database case "<case>"
    Then the catalog matches the stored result

    Examples:
      | case    |
      | partial |
      | absent  |

  @redis
  Scenario: Reserve supplies for pickup
    Given I am a signed-in student
    When I reserve the Redis order "stationery"
    Then the reservation identifies the product and student

