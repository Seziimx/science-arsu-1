// chart анимация появления
window.addEventListener('load', () => {
  const cards = document.querySelectorAll('.chart-card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add('visible');
    }, index * 150);
  });
});

// Chart.js графики
const yearChart = new Chart(document.getElementById('yearChart'), {
  type: 'bar',
  data: {
    labels: year_labels,
    datasets: [{
      label: 'Жыл бойынша',
      data: year_counts,
      backgroundColor: 'rgba(54, 162, 235, 0.7)'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#000'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#000'
        }
      },
      y: {
        ticks: {
          color: '#000'
        }
      }
    }
  }
});

const facultyChart = new Chart(document.getElementById('facultyChart'), {
  type: 'pie',
  data: {
    labels: faculty_labels,
    datasets: [{
      data: faculty_counts,
      backgroundColor: ['#007bff', '#ffc107', '#28a745', '#dc3545', '#6f42c1']
    }]
    },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#000'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#000'
        }
      },
      y: {
        ticks: {
          color: '#000'
        }
      }
    }
  }
});

const typeChart = new Chart(document.getElementById('typeChart'), {
  type: 'bar',
  data: {
    labels: type_labels,
    datasets: [{
      label: 'Жұмыс түрі',
      data: type_counts,
      backgroundColor: 'rgba(255, 99, 132, 0.7)'
    }]
    },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#000'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#000'
        }
      },
      y: {
        ticks: {
          color: '#000'
        }
      }
    }
  }
});

const statusChart = new Chart(document.getElementById('statusChart'), {
  type: 'pie',
  data: {
    labels: status_labels,
    datasets: [{
      data: status_counts,
      backgroundColor: ['#28a745', '#ffc107', '#dc3545']
    }]
    },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#000'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#000'
        }
      },
      y: {
        ticks: {
          color: '#000'
        }
      }
    }
  }
});
