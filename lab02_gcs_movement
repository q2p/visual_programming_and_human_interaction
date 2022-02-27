#define _USE_MATH_DEFINES

#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <random>
#include <cmath>

constexpr double VELOCITY_MAX = 0.8;
constexpr double VELOCITY_DELTA_MAX = 0.2;
constexpr double ANGLE_SWAY_MAX = 0.2;
constexpr double EARTH_RADIUS = 6378137.0;
constexpr double STEPS = 100;

double to_radians(double degrees) {
	return degrees * M_PI / 180.0;
}

class GCS {
	private:
		double lon;
		double lat;
	public:
		GCS(double lon, double lat) {
			this->lon = lon;
			this->lat = lat;
		}
		double get_lon() const {
			return this->lon;
		}
		double get_lat() const {
			return this->lat;
		}
		void set_lon(const double lon) {
			this->lon = lon;
		}
		void set_lat(const double lat) {
			this->lat = lat;
		}
		static double distance_haversine(const GCS& gcs1, const GCS& gcs2) {
				auto lat1 = to_radians(gcs1.get_lat());
				auto lon1 = to_radians(gcs1.get_lon());
				auto lat2 = to_radians(gcs2.get_lat());
				auto lon2 = to_radians(gcs2.get_lon());

				auto lon_d = lon1 - lon2;
				auto lat_d = lat1 - lat2;

				auto a = pow(sin(lat_d / 2.0), 2) + pow(sin(lon_d / 2.0), 2) * cos(lat1) * cos(lat2);
				auto c = 2.0 * asin(sqrt(a));
				return EARTH_RADIUS * c;
		}
};

class Human {
	private:
		uint32_t lifetime = 0;
		std::string first_name;
		std::string last_name;
		std::string patronymic;
		double height;
		double weight;
		double velocity = 0;
		double angle = 0;
		std::vector<GCS> movement_history = std::vector<GCS>();
	public:
		Human(
			const std::string& first_name,
			const std::string& last_name,
			const std::string& patronymic,
			double height,
			double weight,
			const GCS initial_location
		) {
			this->set_first_name(first_name);
			this->set_last_name(last_name);
			this->set_patronymic(patronymic);
			this->height = height;
			this->weight = weight;
			this->move_to(initial_location);
		}
		const std::string& get_first_name() const {
			return this->first_name;
		}
		const std::string& get_last_name() const {
			return this->last_name;
		}
		const std::string& get_patronymic() const {
			return this->patronymic;
		}
		const GCS& get_location() const {
			return this->movement_history.back();
		}
		double get_velocity() const {
			return this->velocity;
		}
		double get_angle() const {
			return this->angle;
		}
		void set_first_name(const std::string& first_name) {
			this->first_name = first_name;
		}
		void set_last_name(const std::string& last_name) {
			this->last_name = last_name;
		}
		void set_patronymic(const std::string& patronymic) {
			this->patronymic = patronymic;
		}
		void move_to(const GCS& location) {
			this->movement_history.push_back(location);
		}
		void increment_lifetime() {
			this->lifetime++;
		}
		void set_velocity(const double velocity) {
			this->velocity = velocity;
		}
		void set_angle(const double angle) {
			this->angle = angle;
		}
		double calculate_walked_distance() const {
			if(this->movement_history.size() < 2) {
				return 0.0;
			}

			double distance = 0.0;

			for(auto i = this->movement_history.begin(); i + 1 != this->movement_history.end(); i++) {
				distance += GCS::distance_haversine(*i, *(i+1));
			}
			
			return distance;
		}
};

int main() {
	std::random_device entropy_random;
	std::default_random_engine random(entropy_random());
	std::uniform_real_distribution<double> angle_dist(-ANGLE_SWAY_MAX, ANGLE_SWAY_MAX);
	std::uniform_real_distribution<double> speed_dist(-VELOCITY_DELTA_MAX, VELOCITY_DELTA_MAX);
	
	auto humans = std::vector<Human>();

	humans.emplace_back("Вася", "Пупкин", "Пупкович", 1.8, 90, GCS(0, 0));
	humans.emplace_back("Валерия", "Пупкина", "Пупковна", 1.7, 80, GCS(0, 0));
	
	for(size_t step = 0; step != STEPS; step++) {
		for (auto& human : humans) {
			human.set_velocity(std::min(VELOCITY_MAX, human.get_velocity() + speed_dist(random)));
			human.set_angle(human.get_angle() + angle_dist(random));
			auto lon = human.get_location().get_lon() + human.get_velocity() * cos(human.get_angle());
			auto lat = human.get_location().get_lat() + human.get_velocity() * sin(human.get_angle());
			human.move_to(GCS(lon, lat));
			human.increment_lifetime();
		}
	}

	for (auto& human : humans) {
		std::cout << human.get_first_name() << " " << human.get_last_name() << " " << human.get_patronymic() << " прошли " << human.calculate_walked_distance() << " метров.\n";
	}

	return 0;
}
